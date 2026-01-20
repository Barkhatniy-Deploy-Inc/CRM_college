from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import HTTPException, status

from database.models import User, RefreshToken
from services.security import create_access_token, create_refresh_token, decode_token
from core.config import settings


def create_token_pair(user: User, db: Session, ip_address: str = None, user_agent: str = None) -> tuple[str, str]:
    """Создание пары access и refresh токенов"""
    # Создание токенов
    access_token = create_access_token({
        "user_id": user.id,
        "email": user.email,
        "role": user.role.value
    })
    
    refresh_token_str = create_refresh_token(user.id)
    
    # Сохранение refresh токена в БД
    payload = decode_token(refresh_token_str)
    refresh_token = RefreshToken(
        user_id=user.id,
        token=refresh_token_str,
        expires_at=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    db.add(refresh_token)
    db.commit()
    
    return access_token, refresh_token_str


def refresh_access_token(refresh_token_str: str, db: Session) -> tuple[str, str, User]:
    """
    Обновление access токена с помощью refresh токена.
    Возвращает новый access токен, refresh токен и пользователя.
    """
    # Декодирование refresh токена
    try:
        payload = decode_token(refresh_token_str)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный refresh токен"
        )
    
    # Проверка типа токена
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный тип токена"
        )
    
    # Поиск токена в БД с join к пользователю (оптимизация - один запрос)
    refresh_token = db.query(RefreshToken).join(User).filter(
        RefreshToken.token == refresh_token_str,
        RefreshToken.is_revoked == False,
        RefreshToken.expires_at > datetime.now(timezone.utc),
        User.is_active == True
    ).first()
    
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh токен не найден, отозван или истек"
        )
    
    user = refresh_token.user
    
    # Обновление времени последнего использования
    refresh_token.last_used_at = datetime.now(timezone.utc)
    db.commit()
    
    # Создание нового access токена
    new_access_token = create_access_token({
        "user_id": user.id,
        "email": user.email,
        "role": user.role.value
    })
    
    return new_access_token, refresh_token_str, user


def revoke_refresh_token(refresh_token_str: str, db: Session) -> None:
    """Отзыв refresh токена"""
    refresh_token = db.query(RefreshToken).filter(
        RefreshToken.token == refresh_token_str
    ).first()
    
    if refresh_token:
        refresh_token.is_revoked = True
        db.commit()


def revoke_all_user_tokens(user_id: int, db: Session) -> None:
    """Отзыв всех токенов пользователя"""
    db.query(RefreshToken).filter(
        RefreshToken.user_id == user_id,
        RefreshToken.is_revoked == False
    ).update({"is_revoked": True})
    db.commit()


def cleanup_expired_tokens(db: Session) -> int:
    """Очистка истекших токенов (можно вызывать периодически)"""
    expired_count = db.query(RefreshToken).filter(
        RefreshToken.expires_at < datetime.now(timezone.utc)
    ).delete()
    
    db.commit()
    return expired_count

