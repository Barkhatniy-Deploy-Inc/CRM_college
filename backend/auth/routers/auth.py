from fastapi import APIRouter, Depends, HTTPException, status, Response, Request, Cookie
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer
from typing import Optional

from database.database import get_db
from database.models import User
from database.schemas import (
    RegisterRequest, LoginRequest, TokenResponse, RefreshTokenRequest,
    UserResponse, PasswordChangeRequest
)
from services.user_service import create_user, authenticate_user
from services.token_service import create_token_pair, refresh_access_token, revoke_refresh_token, revoke_all_user_tokens
from services.security import hash_password, verify_password
from services.cookie_service import set_auth_cookies, clear_auth_cookies
from services.audit_service import log_action, AuditAction
from dependencies import get_current_active_user
from middleware.rate_limit import get_client_ip, get_user_agent
from core.utils import mask_email
from core.config import settings

router = APIRouter(prefix="/api/auth", tags=["🔐 Авторизация"])
security = HTTPBearer()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: RegisterRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Регистрация нового пользователя
    """
    # Создание пользователя
    user = create_user(data, db)
    
    # Получение IP и User-Agent
    ip_address = get_client_ip(request)
    user_agent = get_user_agent(request)
    
    # Создание токенов
    access_token, refresh_token = create_token_pair(user, db, ip_address, user_agent)
    
    # Установка cookies
    set_auth_cookies(response, access_token, refresh_token)
    
    # Логирование в аудит
    log_action(AuditAction.USER_CREATED, user.id, db, {"email": mask_email(user.email), "role": user.role.value}, request)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user)
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Вход в систему
    """
    # Получение IP и User-Agent
    ip_address = get_client_ip(request)
    user_agent = get_user_agent(request)
    
    # Аутентификация
    user = authenticate_user(data.email, data.password, db, ip_address, user_agent)
    
    # Создание токенов
    access_token, refresh_token = create_token_pair(user, db, ip_address, user_agent)
    
    # Установка cookies
    set_auth_cookies(response, access_token, refresh_token)
    
    # Логирование входа в аудит
    log_action(AuditAction.LOGIN, user.id, db, {"ip_address": ip_address}, request)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user)
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    data: Optional[RefreshTokenRequest] = None,
    refresh_token_cookie: Optional[str] = Cookie(None, alias="refresh_token"),
    request: Request = None,
    db: Session = Depends(get_db)
):
    """
    Обновление access токена с помощью refresh токена
    """
    # Приоритет cookie над body
    refresh_token_str = refresh_token_cookie
    if not refresh_token_str and data:
        refresh_token_str = data.refresh_token
    
    if not refresh_token_str:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh токен не предоставлен"
        )
    
    # Обновление токена (внутри функции уже получается пользователь)
    access_token, refresh_token, user = refresh_access_token(refresh_token_str, db)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user) if user else None
    )


@router.post("/logout")
async def logout(
    refresh_token_cookie: Optional[str] = Cookie(None, alias="refresh_token"),
    current_user: User = Depends(get_current_active_user),
    response: Response = Response(),
    request: Request = None,
    db: Session = Depends(get_db)
):
    """
    Выход из системы (отзыв токенов)
    """
    # Отзыв всех токенов пользователя
    revoke_all_user_tokens(current_user.id, db)
    
    # Отзыв конкретного refresh токена если передан
    if refresh_token_cookie:
        revoke_refresh_token(refresh_token_cookie, db)
    
    # Удаление cookies
    clear_auth_cookies(response)
    
    # Логирование выхода в аудит
    log_action(AuditAction.LOGOUT, current_user.id, db, {}, request)
    
    return {"message": "Вы успешно вышли из системы"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Получение информации о текущем пользователе
    """
    return UserResponse.model_validate(current_user)


@router.post("/change-password")
async def change_password(
    data: PasswordChangeRequest,
    current_user: User = Depends(get_current_active_user),
    request: Request = None,
    db: Session = Depends(get_db)
):
    """
    Изменение пароля
    """
    # Проверка текущего пароля
    if not verify_password(data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный текущий пароль"
        )
    
    # Установка нового пароля
    current_user.password_hash = hash_password(data.new_password)
    db.commit()
    
    # Отзыв всех токенов для безопасности
    revoke_all_user_tokens(current_user.id, db)
    
    # Логирование смены пароля в аудит
    log_action(AuditAction.PASSWORD_CHANGE, current_user.id, db, {}, request)
    
    return {"message": "Пароль успешно изменен. Пожалуйста, войдите заново."}

