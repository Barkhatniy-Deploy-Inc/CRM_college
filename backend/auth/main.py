"""
Auth Service - Сервис авторизации и аутентификации
Отвечает за регистрацию, вход, выход и валидацию токенов
"""

from fastapi import FastAPI, HTTPException, Depends, Response, Header, Cookie
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional
import logging

from core.config import settings, LogConfig
from database.database import get_db, engine
from models.user import User, Base
from services.auth_service import AuthService
from api.auth_routes import router as auth_router

# Настройка логирования
LogConfig.configure_logging()
logger = logging.getLogger(__name__)

# Создание таблиц
Base.metadata.create_all(bind=engine)

# Создание FastAPI приложения
app = FastAPI(
    title="CRM College - Auth Service",
    version="1.0.0",
    description="Сервис авторизации и аутентификации для CRM системы колледжа"
)

# CORS настройки
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "Origin", "X-Requested-With"],
    expose_headers=["Content-Disposition"],
)

# Подключение роутеров
app.include_router(auth_router, prefix="/api/auth", tags=["🔐 Авторизация"])

# Health check endpoint
@app.get("/api/health", tags=["🏥 Health"])
async def health_check():
    """Health check endpoint для мониторинга"""
    from datetime import datetime, timezone
    return {
        "status": "healthy",
        "service": "auth-api",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# Endpoint для валидации токенов (для других сервисов)
@app.post("/api/auth/validate", tags=["🔐 Авторизация"])
async def validate_token(
    authorization: Optional[str] = Header(None),
    access_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    """Валидация токена для других сервисов"""
    auth_service = AuthService(db)
    user = await auth_service.get_current_user(authorization, access_token)
    
    return {
        "valid": True,
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": True
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)