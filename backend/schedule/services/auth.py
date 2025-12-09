from datetime import datetime, timedelta, timezone
import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database.models import User
from fastapi import Response, HTTPException
from database.database import get_db
from core.config import settings
import logging

logger = logging.getLogger(__name__)

# Контекст для хеширования паролей с улучшенными настройками безопасности
pwd_context = CryptContext(
    schemes=["bcrypt"], 
    deprecated="auto",
    bcrypt__rounds=12  # Увеличиваем количество раундов для большей безопасности
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля с использованием passlib"""
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """Хеширование пароля с использованием passlib"""
    return pwd_context.hash(password)


def create_access_token(data: dict) -> str:
    """Создание JWT токена с улучшенной безопасностью"""
    if not settings.SECRET_KEY:
        raise ValueError("SECRET_KEY must be set")
    
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),  # Время создания токена
        "iss": "crm-college-api"  # Издатель токена
    })
    
    try:
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    except Exception as e:
        logger.error(f"Error creating access token: {e}")
        raise HTTPException(status_code=500, detail="Could not create access token")


def decode_token(token: str) -> dict:
    """Декодирование JWT токена с улучшенной валидацией"""
    if not token or not isinstance(token, str):
        logger.warning("Invalid token format provided")
        return None
    
    try:
        # Проверяем токен с дополнительными опциями безопасности
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM],
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_iat": True,
                "require": ["exp", "iat", "user_id"]
            }
        )
        
        # Дополнительная проверка издателя
        if payload.get("iss") != "crm-college-api":
            logger.warning("Token issuer mismatch")
            return None
            
        return payload
        
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error decoding token: {e}")
        return None


def set_auth_cookie(response: Response, token: str):
    """Установка cookie с токеном с улучшенными настройками безопасности"""
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,  # Защита от XSS
        max_age=settings.JWT_EXPIRE_MINUTES * 60,
        samesite="strict" if settings.ENVIRONMENT == "production" else "lax",
        secure=settings.ENVIRONMENT == "production",  # HTTPS только в production
        path="/",
        domain=None  # Не устанавливаем domain для безопасности
    )


def create_user(email: str, password: str, full_name: str, db: Session) -> int:
    """Создание нового пользователя"""
    password_hash = hash_password(password)
    new_user = User(email=email, password_hash=password_hash, full_name=full_name)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user.id


def get_user_by_email(email: str, db: Session):
    """Получение пользователя по email"""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(user_id: int, db: Session):
    """Получение пользователя по ID"""
    return db.query(User).filter(User.id == user_id).first()
