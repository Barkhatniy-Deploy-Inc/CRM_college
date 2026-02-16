import logging
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from dotenv import load_dotenv
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend

load_dotenv()

from database.database import init_db
from services.notifications import NOTIFICATIONS_ENABLED
from core.config import LogConfig
from services.websocket_manager import manager
from core.logging_config import setup_logging, get_logger

# Import Routers
from routers import (
    groups, 
    schedule, 
    auditoriums, 
    participants, 
    export, 
    notifications, 
    calendar,
    auth
)

# Инициализируем логирование
setup_logging()
logger = get_logger("main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    LogConfig.configure_logging()
    logger = logging.getLogger(__name__)
    logger.info("Инициализация приложения...")
    init_db()
    FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")
    logger.info("✅ СЕРВЕР ЗАПУЩЕН")
    yield
    await FastAPICache.clear()
    logger.info("✅ СЕРВЕР ОСТАНОВЛЕН")

app = FastAPI(
    title="Умное расписание",
    version="3.2.2",
    lifespan=lifespan,
    description="API для управления учебным расписанием, аудиториями и группами."
)

# CORS settings
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS", 
    "http://localhost:3000,http://localhost:80"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Глобальный Health Check (ПОЛНЫЙ ПУТЬ)
@app.get("/api/schedule/health", tags=["⚙️ Система"])
async def health_check():
    return {"status": "healthy", "service": "Schedule Service"}

# Подключаем роутеры БЕЗ префиксов в include (префиксы будут внутри файлов)
app.include_router(schedule.router)
app.include_router(groups.router)
app.include_router(auditoriums.router)
app.include_router(participants.router)
app.include_router(export.router)
app.include_router(notifications.router)
app.include_router(calendar.router)
app.include_router(auth.router)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logging.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
