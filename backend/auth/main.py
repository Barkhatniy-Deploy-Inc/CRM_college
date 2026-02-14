import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.config import settings
from database.database import init_db
from routers import auth, users
from middleware.rate_limit import RateLimitMiddleware

# Настройка логирования
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    logger.info("🚀 Запуск Auth Service...")
    
    # Инициализация БД
    try:
        init_db()
        logger.info("✅ База данных инициализирована")
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации БД: {e}")
        raise
    
    logger.info("✅ Auth Service запущен")
    yield
    
    logger.info("🛑 Остановка Auth Service...")


# Создание приложения
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Сервис аутентификации и авторизации для CRM College",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,  # Важно для работы с cookies
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],  # Позволяет клиенту видеть все заголовки
)

# Rate limiting middleware
if settings.RATE_LIMIT_ENABLED:
    app.add_middleware(RateLimitMiddleware)


# Обработчик ошибок
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Необработанная ошибка: {exc}", exc_info=settings.DEBUG)
    return JSONResponse(
        status_code=500,
        content={"detail": "Внутренняя ошибка сервера"}
    )


# Health check (перемещен в конец)
@app.get("/health", tags=["⚙️ Система"])
async def health_check():
    """Проверка здоровья сервиса"""
    try:
        # Можно добавить проверку подключения к БД
        return {
            "status": "healthy",
            "service": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )


# Подключение роутеров
app.include_router(auth.router)
app.include_router(users.router)

# Импорт роутера сессий
from routers import sessions
app.include_router(sessions.router)


# ============ Системные эндпоинты (в конце) ============

@app.get("/", tags=["⚙️ Система"])
async def root():
    """Корневой endpoint"""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs" if settings.DEBUG else "disabled"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning"
    )

