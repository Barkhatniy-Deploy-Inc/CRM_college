import os
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # Основные настройки
    APP_NAME: str = "CRM College Auth Service"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("ENVIRONMENT") != "production"
    
    # Безопасность
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "30"))
    
    # Защита от брутфорса
    MAX_LOGIN_ATTEMPTS: int = int(os.getenv("MAX_LOGIN_ATTEMPTS", "5"))
    LOCKOUT_DURATION_MINUTES: int = int(os.getenv("LOCKOUT_DURATION_MINUTES", "30"))
    
    # CORS
    # CORS
    ALLOWED_ORIGINS: Union[List[str], str] = os.getenv(
        "ALLOWED_ORIGINS", 
        "http://localhost:3000,http://localhost:80"
    ).split(",")
    
    # Rate limiting
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_WINDOW_SECONDS: int = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))

    # Внутренний токен для межсервисных вызовов (аудит и т.п.)
    INTERNAL_API_TOKEN: str = os.getenv("INTERNAL_API_TOKEN", "")
    
    # База данных
    # DB_TYPE: "sqlite" для локальной разработки, "postgresql" для production
    DB_TYPE: str = os.getenv("DB_TYPE", "sqlite")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME", os.getenv("AUTH_DB_NAME", "auth_db"))
    # Путь к SQLite файлу (используется только если DB_TYPE=sqlite)
    SQLITE_PATH: str = os.getenv("SQLITE_PATH", "database/auth.db")
    
    # Redis (для rate limiting и кеширования)
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v):
        if isinstance(v, str) and not v.strip().startswith("["):
            return [x.strip() for x in v.split(",")]
        return v
    
    class Config:
        case_sensitive = True


settings = Settings()

# Проверка обязательных параметров
if not settings.SECRET_KEY:
    if settings.ENVIRONMENT == "production":
        raise ValueError("SECRET_KEY must be set in environment variables for production!")
    else:
        # Генерируем временный ключ для development
        import secrets
        settings.SECRET_KEY = secrets.token_hex(32)
        print("⚠️  WARNING: Using auto-generated SECRET_KEY for development. Set SECRET_KEY in .env for production!")

