import logging
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from dotenv import load_dotenv
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend

load_dotenv()

from database.database import init_db, engine
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from fastapi.responses import JSONResponse
from urllib.parse import urlsplit
from services.notifications import NOTIFICATIONS_ENABLED
from core.config import LogConfig
from services.websocket_manager import manager
from dependencies import authenticate_websocket
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
    relations
)

# Инициализируем логирование
setup_logging()
logger = get_logger("main")


def is_allowed_websocket_origin(origin: str | None, host: str | None, forwarded_proto: str | None) -> bool:
    """Require an explicit allowlisted or exact same-origin browser Origin."""
    if not origin or not host:
        return False
    parsed_origin = urlsplit(origin)
    if parsed_origin.scheme not in {"http", "https"} or not parsed_origin.netloc:
        return False
    normalized_origin = f"{parsed_origin.scheme}://{parsed_origin.netloc}".lower()
    allowed_origins = set()
    for value in ALLOWED_ORIGINS:
        parsed_allowed = urlsplit(value.strip())
        if parsed_allowed.scheme and parsed_allowed.netloc:
            allowed_origins.add(f"{parsed_allowed.scheme}://{parsed_allowed.netloc}".lower())
    if normalized_origin in allowed_origins:
        return True

    return bool(
        parsed_origin.netloc.lower() == host.lower()
        and forwarded_proto in {"http", "https"}
        and parsed_origin.scheme == forwarded_proto
    )

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
def health_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return JSONResponse(status_code=503, content={"status": "unhealthy", "service": "Schedule Service"})
    return {"status": "healthy", "service": "Schedule Service"}

# Подключаем роутеры БЕЗ дополнительных префиксов (они заданы внутри файлов)
# Register the static dictionary routes before /api/schedule/{lesson_id}.
app.include_router(groups.router)
app.include_router(auditoriums.router)
app.include_router(participants.router)
app.include_router(export.router)
app.include_router(notifications.router)
app.include_router(calendar.router)
app.include_router(relations.router)
app.include_router(schedule.router)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    origin = websocket.headers.get("origin")
    host = websocket.headers.get("x-forwarded-host") or websocket.headers.get("host")
    forwarded_proto = websocket.headers.get("x-forwarded-proto", "").split(",", 1)[0].strip()
    if not is_allowed_websocket_origin(origin, host, forwarded_proto):
        await websocket.close(code=1008, reason="Origin is not allowed")
        return
    try:
        await authenticate_websocket(websocket)
    except HTTPException:
        await websocket.close(code=1008, reason="Authentication required")
        return
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive()
    except WebSocketDisconnect:
        pass
    except Exception:
        logger.exception("WebSocket connection failed")
    finally:
        manager.disconnect(websocket)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
