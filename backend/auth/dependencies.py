from fastapi import Depends, HTTPException, status, Header, Cookie
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
import hmac

from database.database import get_db
from database.models import User, UserRole, Permission
from services.security import verify_token
from services.user_service import get_user_by_id, get_user_permissions
from core.config import settings


security = HTTPBearer(auto_error=False)  # Не выбрасываем ошибку автоматически


async def get_current_user(
    access_token: Optional[str] = Cookie(None, alias="access_token"),
    authorization: Optional[str] = Header(None),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Зависимость для получения текущего пользователя из токена.
    Поддерживает Bearer токен из заголовка Authorization или cookie.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Приоритет: cookie > Authorization header > HTTPBearer
    token = None
    token_source = None
    
    if access_token:
        token = access_token
        token_source = "cookie"
    elif authorization and " " in authorization:
        token = authorization.split()[1]
        token_source = "header"
    elif credentials:
        token = credentials.credentials
        token_source = "bearer"
    
    if not token:
        logger.warning("Токен не найден. Cookie: %s, Header: %s, Bearer: %s", 
                      bool(access_token), bool(authorization), bool(credentials))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен не предоставлен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.debug(f"Токен получен из {token_source}, длина: {len(token)}")
    
    # Верификация токена
    try:
        token_data = verify_token(token)
    except HTTPException as e:
        logger.warning(f"Ошибка верификации токена: {e.detail}")
        raise
    
    # Получение пользователя из БД
    user = get_user_by_id(token_data.user_id, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Аккаунт деактивирован"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Зависимость для получения активного пользователя"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Аккаунт деактивирован"
        )
    return current_user


def require_role(*allowed_roles: UserRole):
    """Зависимость для проверки роли пользователя"""
    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Требуется одна из ролей: {', '.join([r.value for r in allowed_roles])}"
            )
        return current_user
    return role_checker


async def require_internal_token(
    x_internal_token: Optional[str] = Header(None, alias="X-Internal-Token"),
) -> None:
    """
    Проверка внутреннего токена для межсервисных вызовов.

    Если токен не сконфигурирован, endpoint недоступен (503), чтобы
    не оставлять внутренний API открытым по умолчанию.
    """
    if not settings.INTERNAL_API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Internal API token is not configured",
        )
    if not x_internal_token or not hmac.compare_digest(
        x_internal_token, settings.INTERNAL_API_TOKEN
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid internal token",
        )


def require_permission(resource: str, action: str):
    """Зависимость для проверки разрешения пользователя"""
    def permission_checker(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ) -> User:
        # Админы имеют все права
        if current_user.role == UserRole.ADMIN:
            return current_user
        
        # Проверка разрешений пользователя
        permissions = get_user_permissions(current_user.id, db)
        for perm in permissions:
            if perm.resource == resource and perm.action == action:
                return current_user
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Недостаточно прав для выполнения действия {action} на ресурсе {resource}"
        )
    return permission_checker

