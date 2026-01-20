from datetime import datetime, timedelta, timezone
import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database.models import User
from fastapi import Response, Depends
from database.database import get_db
import os
import secrets

# Настройки безопасности из .env
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_hex(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24 * 7))

# Контекст для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля с использованием passlib"""
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """Хеширование пароля с использованием passlib"""
    return pwd_context.hash(password)


def create_access_token(data: dict) -> str:
    """Создание JWT токена"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    """Декодирование JWT токена"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def set_auth_cookie(response: Response, token: str):
    """Установка cookie с токеном"""
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=os.getenv("ENVIRONMENT") == "production",
        path="/"
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
