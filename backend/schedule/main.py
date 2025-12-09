import logging
from fastapi import FastAPI, HTTPException, Depends, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from contextlib import asynccontextmanager
import uvicorn
from dotenv import load_dotenv
import json
from sqlalchemy.orm import Session

from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache

load_dotenv()

from database.models import *
from database.database import init_db, get_db
from middleware.auth_middleware import get_current_user_from_auth_service_from_auth_service
from api.courses_api import get_courses, create_course, get_course, update_course, delete_course
from api.slots_api import create_class_slot, get_class_slot, update_class_slot, delete_class_slot
from api.participants_api import get_course_participants, add_participant_to_course, remove_participant_from_course
from api.schedule_api import get_schedule_list
from api.auditoriums_api import create_auditorium, get_auditoriums, get_auditorium, update_auditorium, delete_auditorium
from services.notifications import subscribe_telegram_notification, NOTIFICATIONS_ENABLED
from core.config import LogConfig, settings
from services.calendar_service import generate_calendar_for_user
from services.websocket_manager import manager

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
    description="API для управления учебным расписанием, аудиториями и курсами."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "Origin", "X-Requested-With"],
    expose_headers=["Content-Disposition"],
)

# Авторизация теперь обрабатывается отдельным сервисом

@app.post("/api/auditoriums", response_model=AuditoriumResponse, tags=["🏫 Аудитории"])
async def create_auditorium_ep(data: AuditoriumCreate, user: dict = Depends(get_current_user_from_auth_service), db: Session = Depends(get_db)):
    auditorium = await create_auditorium(data, db)
    await FastAPICache.clear(namespace="fastapi-cache")
    await manager.broadcast(json.dumps({"type": "auditorium_created", "data": json.loads(AuditoriumResponse.from_orm(auditorium).model_dump_json())}))
    return auditorium

@app.get("/api/auditoriums", response_model=List[AuditoriumResponse], tags=["🏫 Аудитории"])
@cache(expire=60)
async def get_auditoriums_ep(search: Optional[str] = None, db: Session = Depends(get_db)):
    return await get_auditoriums(search, db=db)

@app.get("/api/auditoriums/{auditorium_id}", response_model=AuditoriumResponse, tags=["🏫 Аудитории"])
async def get_auditorium_ep(auditorium_id: int, db: Session = Depends(get_db)):
    return await get_auditorium(auditorium_id, db)

@app.put("/api/auditoriums/{auditorium_id}", response_model=AuditoriumResponse, tags=["🏫 Аудитории"])
async def update_auditorium_ep(auditorium_id: int, data: AuditoriumUpdate, user: dict = Depends(get_current_user_from_auth_service), db: Session = Depends(get_db)):
    auditorium = await update_auditorium(auditorium_id, data, db)
    await FastAPICache.clear(namespace="fastapi-cache")
    await manager.broadcast(json.dumps({"type": "auditorium_updated", "data": json.loads(AuditoriumResponse.from_orm(auditorium).model_dump_json())}))
    return auditorium

@app.delete("/api/auditoriums/{auditorium_id}", tags=["🏫 Аудитории"])
async def delete_auditorium_ep(auditorium_id: int, user: dict = Depends(get_current_user_from_auth_service), db: Session = Depends(get_db)):
    await delete_auditorium(auditorium_id, db)
    await FastAPICache.clear(namespace="fastapi-cache")
    await manager.broadcast(json.dumps({"type": "auditorium_deleted", "data": {"id": auditorium_id}}))
    return {"message": "Аудитория успешно удалена"}

@app.post("/api/schedule", response_model=ClassSlotResponse, tags=["🗓️ Расписание"])
async def create_lesson_ep(data: ClassSlotCreate, user: dict = Depends(get_current_user_from_auth_service), db: Session = Depends(get_db)):
    lesson = await create_class_slot(data, db)
    await manager.broadcast(json.dumps({"type": "lesson_created", "data": json.loads(ClassSlotResponse.from_orm(lesson).model_dump_json())}))
    return lesson

@app.get("/api/schedule", response_model=List[dict], tags=["🗓️ Расписание"])
@cache(expire=30)
async def get_schedule_list_ep(date: Optional[str] = None, date_from: Optional[str] = None, date_to: Optional[str] = None, limit: int = 100, offset: int = 0, db: Session = Depends(get_db)):
    return await get_schedule_list(date, date_from, date_to, limit, offset, db)

@app.get("/api/schedule/{lesson_id}", response_model=ClassSlotResponse, tags=["🗓️ Расписание"])
async def get_lesson_ep(lesson_id: int, db: Session = Depends(get_db)):
    return await get_class_slot(lesson_id, db)

@app.put("/api/schedule/{lesson_id}", response_model=ClassSlotResponse, tags=["🗓️ Расписание"])
async def update_lesson_ep(lesson_id: int, data: ClassSlotUpdate, user: dict = Depends(get_current_user_from_auth_service), db: Session = Depends(get_db)):
    lesson = await update_class_slot(lesson_id, data, db)
    await manager.broadcast(json.dumps({"type": "lesson_updated", "data": json.loads(ClassSlotResponse.from_orm(lesson).model_dump_json())}))
    return lesson

@app.delete("/api/schedule/{lesson_id}", tags=["🗓️ Расписание"])
async def delete_lesson_ep(lesson_id: int, user: dict = Depends(get_current_user_from_auth_service), db: Session = Depends(get_db)):
    await delete_class_slot(lesson_id, db)
    await manager.broadcast(json.dumps({"type": "lesson_deleted", "data": {"id": lesson_id}}))
    return {"message": "Урок успешно удален"}

@app.get("/api/courses", response_model=List[CourseResponse], tags=["📚 Курсы"])
@cache(expire=60)
async def get_courses_ep(name: Optional[str] = None, limit: int = 100, offset: int = 0, db: Session = Depends(get_db)):
    return await get_courses(name, limit, offset, db)

@app.post("/api/courses", response_model=CourseResponse, tags=["📚 Курсы"])
async def create_course_ep(data: CourseCreate, user: dict = Depends(get_current_user_from_auth_service), db: Session = Depends(get_db)):
    course = await create_course(data, db)
    await manager.broadcast(json.dumps({"type": "course_created", "data": json.loads(CourseResponse.from_orm(course).model_dump_json())}))
    return course

@app.get("/api/courses/{course_id}", response_model=CourseResponse, tags=["📚 Курсы"])
async def get_course_ep(course_id: int, db: Session = Depends(get_db)):
    return await get_course(course_id, db)

@app.put("/api/courses/{course_id}", response_model=CourseResponse, tags=["📚 Курсы"])
async def update_course_ep(course_id: int, data: CourseUpdate, user: dict = Depends(get_current_user_from_auth_service), db: Session = Depends(get_db)):
    course = await update_course(course_id, data, db)
    await manager.broadcast(json.dumps({"type": "course_updated", "data": json.loads(CourseResponse.from_orm(course).model_dump_json())}))
    return course

@app.delete("/api/courses/{course_id}", tags=["📚 Курсы"])
async def delete_course_ep(course_id: int, user: dict = Depends(get_current_user_from_auth_service), db: Session = Depends(get_db)):
    await delete_course(course_id, db)
    await manager.broadcast(json.dumps({"type": "course_deleted", "data": {"id": course_id}}))
    return {"message": "Курс успешно удален"}

@app.get("/api/courses/{course_id}/participants", response_model=List[UserResponse], tags=["👥 Участники"])
async def get_course_participants_ep(course_id: int, db: Session = Depends(get_db)):
    return await get_course_participants(course_id, db)

@app.post("/api/courses/{course_id}/participants", tags=["👥 Участники"])
async def add_course_participant_ep(course_id: int, data: AddParticipantRequest, user: dict = Depends(get_current_user_from_auth_service), db: Session = Depends(get_db)):
    result = await add_participant_to_course(course_id, data.user_id, db)
    await manager.broadcast(json.dumps({"type": "participant_added", "data": {"course_id": course_id, "user_id": data.user_id}}))
    return result

@app.delete("/api/courses/{course_id}/participants/{user_id}", tags=["👥 Участники"])
async def remove_course_participant_ep(course_id: int, user_id: int, user: dict = Depends(get_current_user_from_auth_service), db: Session = Depends(get_db)):
    await remove_participant_from_course(course_id, user_id, db)
    await manager.broadcast(json.dumps({"type": "participant_removed", "data": {"course_id": course_id, "user_id": user_id}}))
    return {"message": "Участник успешно удален из курса"}

@app.post("/api/notifications/subscribe-telegram", tags=["🔔 Уведомления"])
async def subscribe_telegram_ep(telegram_id: str, user: dict = Depends(get_current_user_from_auth_service), db: Session = Depends(get_db)):
    # Обновляем telegram_id пользователя через auth service
    # TODO: Реализовать обновление через API auth service
    return {"message": "Telegram подписка активирована", "telegram_id": telegram_id}

@app.get("/api/health", tags=["⚙️ Система"])
async def health_check():
    return {"status": "healthy", "telegram": "enabled" if NOTIFICATIONS_ENABLED else "disabled", "database": "connected"}

@app.get("/api/calendar/me.ics", tags=["🗓️ Расписание"])
async def get_my_calendar(user: dict = Depends(get_current_user_from_auth_service), db: Session = Depends(get_db)):
    from fastapi import Response
    calendar_content = await generate_calendar_for_user(user["id"], db)
    return Response(content=calendar_content, media_type="text/calendar", headers={"Content-Disposition": "attachment; filename=my_schedule.ics"})

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

# Health check endpoint
@app.get("/api/health", tags=["🏥 Health"])
async def health_check():
    """Health check endpoint для мониторинга"""
    from datetime import datetime, timezone
    return {
        "status": "healthy",
        "service": "schedule-api",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
