from datetime import datetime, timedelta, timezone
import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import HTTPException, Response
from core.config import settings
from models.user import User
import logging

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        # Контекст для хеширования паролей с улучшенными настройками безопасности
        self.pwd_context = CryptContext(
            schemes=["bcrypt"], 
            deprecated="auto",
            bcrypt__rounds=12  # Увеличиваем количество раундов для большей безопасности
        )

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Проверка пароля с использованием passlib"""
        return self.pwd_context.verify(plain_password, hashed_password)

    def hash_password(self, password: str) -> str:
        """Хеширование пароля с использованием passlib"""
        return self.pwd_context.hash(password)

    def create_access_token(self, data: dict) -> str:
        """Создание JWT токена с улучшенной безопасностью"""
        if not settings.SECRET_KEY:
            raise ValueError("SECRET_KEY must be set")
        
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc),  # Время создания токена
            "iss": "crm-college-auth"  # Издатель токена
        })
        
        try:
            return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        except Exception as e:
            logger.error(f"Error creating access token: {e}")
            raise HTTPException(status_code=500, detail="Could not create access token")

    def decode_token(self, token: str) -> dict:
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
            if payload.get("iss") != "crm-college-auth":
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

    def set_auth_cookie(self, response: Response, token: str):
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

    def create_user(self, email: str, password: str, full_name: str) -> int:
        """Создание нового пользователя"""
        password_hash = self.hash_password(password)
        new_user = User(email=email, password_hash=password_hash, full_name=full_name)
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user.id

    def get_user_by_email(self, email: str) -> User:
        """Получение пользователя по email"""
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_id(self, user_id: int) -> User:
        """Получение пользователя по ID"""
        return self.db.query(User).filter(User.id == user_id).first()

    async def get_current_user(self, authorization: str = None, access_token: str = None) -> User:
        """Безопасное получение текущего пользователя с улучшенной валидацией"""
        token = None
        
        # Безопасное извлечение токена из заголовка Authorization
        if authorization:
            try:
                scheme, token_value = authorization.split(" ", 1)
                if scheme.lower() == "bearer":
                    token = token_value
            except ValueError:
                pass  # Неправильный формат заголовка
        
        # Если токена нет в заголовке, проверяем cookie
        if not token:
            token = access_token
        
        if not token:
            raise HTTPException(
                status_code=401, 
                detail="Токен авторизации не предоставлен",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Декодируем и валидируем токен
        payload = self.decode_token(token)
        if not payload:
            raise HTTPException(
                status_code=401, 
                detail="Невалидный или истекший токен",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Получаем пользователя из базы данных
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Токен не содержит ID пользователя")
        
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                raise HTTPException(status_code=401, detail="Пользователь не найден")
            return user
        except Exception as e:
            logger.error(f"Database error while getting user {user_id}: {e}")
            raise HTTPException(status_code=500, detail="Ошибка при получении данных пользователя")

    def authenticate_user(self, email: str, password: str) -> User:
        """Аутентификация пользователя"""
        user = self.get_user_by_email(email)
        if not user:
            return None
        if not self.verify_password(password, user.password_hash):
            return None
        return user