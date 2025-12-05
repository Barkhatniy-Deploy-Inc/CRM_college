import logging
from fastapi import FastAPI, HTTPException, Depends, Header, Response, Cookie, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from contextlib import asynccontextmanager
import uvicorn
from dotenv import load_dotenv
import json
import sys
import os

# Добавляем текущую директорию в sys.path, чтобы Python мог найти модули
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache

# Загружаем .env
load_dotenv()

# ========== ИМПОРТЫ ==========
from schedule.database.models import *
from schedule.services.auth import create_user, get_user_by_email, get_user_by_id, verify_password, create_access_token, decode_token, set_auth_cookie
from schedule.database.database import init_db
from schedule.api.courses_api import get_courses, create_course, get_course, update_course, delete_course
from schedule.api.slots_api import create_class_slot, get_class_slot, update_class_slot, delete_class_slot
from schedule.api.participants_api import get_course_participants, add_participant_to_course, remove_participant_from_course
from schedule.api.schedule_api import get_schedule_list
from schedule.api.auditoriums_api import create_auditorium, get_auditoriums, get_auditorium, update_auditorium, delete_auditorium
from schedule.services.notifications import subscribe_telegram_notification, NOTIFICATIONS_ENABLED
from schedule.core.config import LogConfig
from schedule.services.calendar_service import generate_calendar_for_user
from schedule.services.websocket_manager import manager

# ========== LIFESPAN MANAGER ==========
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управляет жизненным циклом приложения: инициализация БД, логирования и кэширования при старте."""
    LogConfig.configure_logging()
    logger = logging.getLogger(__name__)
    logger.info("Инициализация приложения...")
    init_db()
    FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")
    logger.info("✅ СЕРВЕР ЗАПУЩЕН")
    yield
    await FastAPICache.clear()
    logger.info("✅ СЕРВЕР ОСТАНОВЛЕН")

# ========== ПРИЛОЖЕНИЕ ==========
app = FastAPI(
    title="Умное расписание",
    version="3.2.2",
    lifespan=lifespan,
    description="API для управления учебным расписанием, аудиториями и курсами."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== ЗАВИСИМОСТИ ==========
async def get_current_user(authorization: Optional[str] = Header(None), access_token: Optional[str] = Cookie(None)) -> dict:
    """Получает текущего пользователя из токена в заголовке или cookie."""
    token = access_token or (authorization.split()[1] if authorization and " " in authorization else None)
    if not token:
        raise HTTPException(status_code=401, detail="Не аутентифицирован")
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Невалидный токен")
    user = get_user_by_id(payload.get("user_id"))
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    return user

# ========== ЭНДПОИНТЫ АВТОРИЗАЦИИ ==========
@app.post("/api/auth/register", response_model=TokenResponse, tags=["🔐 Авторизация"])
async def register(data: RegisterRequest, response: Response):
    """Регистрация нового пользователя."""
    if get_user_by_email(data.email):
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")
    user_id = create_user(data.email, data.password, data.full_name)
    token = create_access_token({"user_id": user_id})
    user_info = {"id": user_id, "email": data.email, "full_name": data.full_name}
    set_auth_cookie(response, token)
    return TokenResponse(access_token=token, user=UserResponse.model_validate(user_info))

@app.post("/api/auth/login", response_model=TokenResponse, tags=["🔐 Авторизация"])
async def login(data: LoginRequest, response: Response):
    """Вход пользователя в систему."""
    user = get_user_by_email(data.email)
    if not user or not verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Неверные учетные данные")
    token = create_access_token({"user_id": user["id"]})
    set_auth_cookie(response, token)
    return TokenResponse(access_token=token, user=UserResponse.model_validate(user))

@app.get("/api/auth/me", response_model=UserResponse, tags=["🔐 Авторизация"])
async def get_me(u: dict = Depends(get_current_user)):
    """Получение информации о текущем пользователе."""
    return UserResponse.model_validate(u)

@app.post("/api/auth/logout", tags=["🔐 Авторизация"])
async def logout(response: Response):
    """Выход пользователя из системы."""
    response.delete_cookie("access_token")
    return {"message": "Вы успешно вышли из системы"}

# ========== ЭНДПОИНТЫ АУДИТОРИЙ ==========
@app.post("/api/auditoriums", response_model=AuditoriumResponse, tags=["🏫 Аудитории"])
async def create_auditorium_ep(data: AuditoriumCreate, u: dict = Depends(get_current_user)):
    """Создать новую аудиторию."""
    auditorium = await create_auditorium(data)
    await FastAPICache.clear(namespace="fastapi-cache")
    await manager.broadcast(json.dumps({"type": "auditorium_created", "data": json.loads(auditorium.model_dump_json())}))
    return auditorium

@app.get("/api/auditoriums", response_model=List[AuditoriumResponse], tags=["🏫 Аудитории"])
@cache(expire=60)
async def get_auditoriums_ep(search: Optional[str] = None):
    """Получить список аудиторий (с возможностью поиска)."""
    return await get_auditoriums(search)

@app.get("/api/auditoriums/{auditorium_id}", response_model=AuditoriumResponse, tags=["🏫 Аудитории"])
async def get_auditorium_ep(auditorium_id: int):
    """Получить информацию об одной аудитории по ID."""
    return await get_auditorium(auditorium_id)

@app.put("/api/auditoriums/{auditorium_id}", response_model=AuditoriumResponse, tags=["🏫 Аудитории"])
async def update_auditorium_ep(auditorium_id: int, data: AuditoriumUpdate, u: dict = Depends(get_current_user)):
    """Обновить информацию об аудитории."""
    auditorium = await update_auditorium(auditorium_id, data)
    await FastAPICache.clear(namespace="fastapi-cache")
    await manager.broadcast(json.dumps({"type": "auditorium_updated", "data": json.loads(auditorium.model_dump_json())}))
    return auditorium

@app.delete("/api/auditoriums/{auditorium_id}", tags=["🏫 Аудитории"])
async def delete_auditorium_ep(auditorium_id: int, u: dict = Depends(get_current_user)):
    """Удалить аудиторию."""
    await delete_auditorium(auditorium_id)
    await FastAPICache.clear(namespace="fastapi-cache")
    await manager.broadcast(json.dumps({"type": "auditorium_deleted", "data": {"id": auditorium_id}}))
    return {"message": "Аудитория успешно удалена"}

# ========== ЭНДПОИНТЫ РАСПИСАНИЯ (УРОКОВ) ==========
@app.post("/api/schedule", response_model=ClassSlotResponse, tags=["🗓️ Расписание"])
async def create_lesson_ep(data: ClassSlotCreate, u: dict = Depends(get_current_user)):
    """Создать новый урок в расписании."""
    lesson = await create_class_slot(data)
    await manager.broadcast(json.dumps({"type": "lesson_created", "data": json.loads(lesson.model_dump_json())}))
    return lesson

@app.get("/api/schedule", response_model=List[dict], tags=["🗓️ Расписание"])
@cache(expire=30)
async def get_schedule_list_ep(date: Optional[str] = None, date_from: Optional[str] = None, date_to: Optional[str] = None, limit: int = 100, offset: int = 0):
    """Получить список уроков с фильтрами."""
    return await get_schedule_list(date, date_from, date_to, limit, offset)

@app.get("/api/schedule/{lesson_id}", response_model=ClassSlotResponse, tags=["🗓️ Расписание"])
async def get_lesson_ep(lesson_id: int):
    """Получить один урок по ID."""
    return await get_class_slot(lesson_id)

@app.put("/api/schedule/{lesson_id}", response_model=ClassSlotResponse, tags=["🗓️ Расписание"])
async def update_lesson_ep(lesson_id: int, data: ClassSlotUpdate, u: dict = Depends(get_current_user)):
    """Обновить урок."""
    lesson = await update_class_slot(lesson_id, data)
    await manager.broadcast(json.dumps({"type": "lesson_updated", "data": json.loads(lesson.model_dump_json())}))
    return lesson

@app.delete("/api/schedule/{lesson_id}", tags=["🗓️ Расписание"])
async def delete_lesson_ep(lesson_id: int, u: dict = Depends(get_current_user)):
    """Удалить урок."""
    await delete_class_slot(lesson_id)
    await manager.broadcast(json.dumps({"type": "lesson_deleted", "data": {"id": lesson_id}}))
    return {"message": "Урок успешно удален"}

# ========== ЭНДПОИНТЫ КУРСОВ ==========
@app.get("/api/courses", response_model=List[CourseResponse], tags=["📚 Курсы"])
@cache(expire=60)
async def get_courses_ep(name: Optional[str] = None, limit: int = 100, offset: int = 0):
    """Получить список курсов."""
    return await get_courses(name, limit, offset)

@app.post("/api/courses", response_model=CourseResponse, tags=["📚 Курсы"])
async def create_course_ep(data: CourseCreate, u: dict = Depends(get_current_user)):
    """Создать новый курс."""
    course = await create_course(data)
    await manager.broadcast(json.dumps({"type": "course_created", "data": json.loads(course.model_dump_json())}))
    return course

@app.get("/api/courses/{course_id}", response_model=CourseResponse, tags=["📚 Курсы"])
async def get_course_ep(course_id: int):
    """Получить один курс по ID."""
    return await get_course(course_id)

@app.put("/api/courses/{course_id}", response_model=CourseResponse, tags=["📚 Курсы"])
async def update_course_ep(course_id: int, data: CourseUpdate, u: dict = Depends(get_current_user)):
    """Обновить курс."""
    course = await update_course(course_id, data)
    await manager.broadcast(json.dumps({"type": "course_updated", "data": json.loads(course.model_dump_json())}))
    return course

@app.delete("/api/courses/{course_id}", tags=["📚 Курсы"])
async def delete_course_ep(course_id: int, u: dict = Depends(get_current_user)):
    """Удалить курс."""
    await delete_course(course_id)
    await manager.broadcast(json.dumps({"type": "course_deleted", "data": {"id": course_id}}))
    return {"message": "Курс успешно удален"}

# ========== ЭНДПОИНТЫ УЧАСТНИКОВ ==========
@app.get("/api/courses/{course_id}/participants", response_model=List[UserResponse], tags=["👥 Участники"])
async def get_course_participants_ep(course_id: int):
    """Получить список участников курса."""
    return await get_course_participants(course_id)

@app.post("/api/courses/{course_id}/participants", tags=["👥 Участники"])
async def add_course_participant_ep(course_id: int, data: AddParticipantRequest, u: dict = Depends(get_current_user)):
    """Добавить участника к курсу."""
    result = await add_participant_to_course(course_id, data.user_id)
    await manager.broadcast(json.dumps({"type": "participant_added", "data": {"course_id": course_id, "user_id": data.user_id}}))
    return result

@app.delete("/api/courses/{course_id}/participants/{user_id}", tags=["👥 Участники"])
async def remove_course_participant_ep(course_id: int, user_id: int, u: dict = Depends(get_current_user)):
    """Удалить участника из курса."""
    await remove_participant_from_course(course_id, user_id)
    await manager.broadcast(json.dumps({"type": "participant_removed", "data": {"course_id": course_id, "user_id": user_id}}))
    return {"message": "Участник успешно удален из курса"}

# ========== ПРОЧИЕ ЭНДПОИНТЫ ==========
@app.post("/api/notifications/subscribe-telegram", tags=["🔔 Уведомления"])
async def subscribe_telegram_ep(telegram_id: str, u: dict = Depends(get_current_user)):
    """Подписать текущего пользователя на уведомления в Telegram."""
    return await subscribe_telegram_notification(u['id'], telegram_id)

@app.get("/api/health", tags=["⚙️ Система"])
async def health_check():
    """Проверка состояния сервиса."""
    return {"status": "healthy", "telegram": "enabled" if NOTIFICATIONS_ENABLED else "disabled", "database": "connected"}

@app.get("/api/calendar/me.ics", tags=["🗓️ Расписание"])
async def get_my_calendar(user: dict = Depends(get_current_user)):
    """Получить календарь текущего пользователя в формате .ics."""
    calendar_content = await generate_calendar_for_user(user["id"])
    return Response(content=calendar_content, media_type="text/calendar", headers={"Content-Disposition": "attachment; filename=my_schedule.ics"})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket эндпоинт для real-time обновлений."""
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logging.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

# ========== ЗАПУСК ==========
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
