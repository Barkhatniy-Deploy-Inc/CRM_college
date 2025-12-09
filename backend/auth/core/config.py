import logging
import os
from logging.config import dictConfig
from typing import List
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """
    Application settings with secure defaults and environment variable support.
    """
    # Database
    DB_HOST: str = os.getenv("DB_HOST")
    DB_PORT: int = int(os.getenv("DB_PORT"))
    DB_NAME: str = os.getenv("DB_NAME")
    DB_USER: str = os.getenv("DB_USER")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM")
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES"))
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT")
    DEBUG: bool = os.getenv("DEBUG").lower() == "true"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = os.getenv("ALLOWED_ORIGINS").split(",")
    
    # Services URLs
    SCHEDULE_SERVICE_URL: str = os.getenv("SCHEDULE_SERVICE_URL")
    TECHCARD_SERVICE_URL: str = os.getenv("TECHCARD_SERVICE_URL")
    
    @property
    def database_url(self) -> str:
        """Construct database URL from components."""
        if not self.DB_PASSWORD:
            raise ValueError("DB_PASSWORD environment variable is required")
        return f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    def validate_required_settings(self):
        """Validate that all required settings are present."""
        required_settings = [
            ("SECRET_KEY", self.SECRET_KEY),
            ("DB_PASSWORD", self.DB_PASSWORD),
        ]
        
        missing = [name for name, value in required_settings if not value]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

# Global settings instance
settings = Settings()

class LogConfig:
    """
    Logging configuration for the application.
    """
    LOGGING_LEVEL = logging.DEBUG if settings.DEBUG else logging.INFO
    LOGGING_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    @staticmethod
    def configure_logging():
        dictConfig({
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'default': {
                    'format': LogConfig.LOGGING_FORMAT,
                },
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'formatter': 'default',
                    'stream': 'ext://sys.stdout',
                },
            },
            'root': {
                'level': LogConfig.LOGGING_LEVEL,
                'handlers': ['console'],
            },
        })