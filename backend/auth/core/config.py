import os
from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # Основные настройки
    APP_NAME: str = "CRM College Auth Service"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Безопасность
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # Защита от брутфорса
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:80"]
    
    # Rate limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 60
    
    # База данных
    # DB_TYPE: "sqlite" для локальной разработки, "postgresql" для production
    DB_TYPE: str = "sqlite"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = ""
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    DB_NAME: str = "auth_db"
    # Путь к SQLite файлу (используется только если DB_TYPE=sqlite)
    SQLITE_PATH: str = "database/auth.db"
    
    # Redis (для rate limiting и кеширования)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    class Config:
        env_file = ".env"
        case_sensitive = True
        
    def __init__(self, **values):
        super().__init__(**values)
        
        # Устанавливаем значения из переменных окружения
        self.ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
        self.DEBUG = os.getenv("ENVIRONMENT", "development") != "production"
        
        self.SECRET_KEY = os.getenv("SECRET_KEY", self.SECRET_KEY)
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", str(self.ACCESS_TOKEN_EXPIRE_MINUTES)))
        self.REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", str(self.REFRESH_TOKEN_EXPIRE_DAYS)))
        self.MAX_LOGIN_ATTEMPTS = int(os.getenv("MAX_LOGIN_ATTEMPTS", str(self.MAX_LOGIN_ATTEMPTS)))
        self.LOCKOUT_DURATION_MINUTES = int(os.getenv("LOCKOUT_DURATION_MINUTES", str(self.LOCKOUT_DURATION_MINUTES)))
        
        # Обработка ALLOWED_ORIGINS
        origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:80")
        if origins_str:
            self.ALLOWED_ORIGINS = [origin.strip() for origin in origins_str.split(",") if origin.strip()]
        else:
            self.ALLOWED_ORIGINS = []
        
        self.RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", str(self.RATE_LIMIT_ENABLED)).lower() == "true"
        self.RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", str(self.RATE_LIMIT_REQUESTS)))
        self.RATE_LIMIT_WINDOW_SECONDS = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", str(self.RATE_LIMIT_WINDOW_SECONDS)))
        
        self.DB_TYPE = os.getenv("DB_TYPE", self.DB_TYPE)
        self.DB_USER = os.getenv("DB_USER", self.DB_USER)
        self.DB_PASSWORD = os.getenv("DB_PASSWORD", self.DB_PASSWORD)
        self.DB_HOST = os.getenv("DB_HOST", self.DB_HOST)
        self.DB_PORT = os.getenv("DB_PORT", self.DB_PORT)
        self.DB_NAME = os.getenv("DB_NAME", os.getenv("AUTH_DB_NAME", self.DB_NAME))
        self.SQLITE_PATH = os.getenv("SQLITE_PATH", self.SQLITE_PATH)
        
        self.REDIS_HOST = os.getenv("REDIS_HOST", self.REDIS_HOST)
        self.REDIS_PORT = int(os.getenv("REDIS_PORT", str(self.REDIS_PORT)))
        self.REDIS_DB = int(os.getenv("REDIS_DB", str(self.REDIS_DB)))


settings = Settings()

# Проверка обязательных параметров
if not settings.SECRET_KEY:
    if hasattr(settings, 'ENVIRONMENT') and settings.ENVIRONMENT == "production":
        raise ValueError("SECRET_KEY must be set in environment variables for production!")
    else:
        # Генерируем временный ключ для development
        import secrets
        settings.SECRET_KEY = secrets.token_hex(32)
        print("⚠️  WARNING: Using auto-generated SECRET_KEY for development. Set SECRET_KEY in .env for production!")

