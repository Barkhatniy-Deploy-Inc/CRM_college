import logging
from fastapi import FastAPI, HTTPException, Depends, Header, Response, Cookie, WebSocket, WebSocketDisconnect, UploadFile, File
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
from services.auth import create_user, get_user_by_email, get_user_by_id, verify_password, create_access_token, decode_token, set_auth_cookie
from database.database import init_db, get_db
from api.groups_api import get_groups, create_group, get_group, update_group, delete_group
from api.slots_api import create_class_slot, get_class_slot, update_class_slot, delete_class_slot
from api.participants_api import get_group_participants, add_participant_to_group, remove_participant_from_group
from api.schedule_api import get_schedule_list, upload_schedule
from api.export_api import export_schedule_xlsx, export_schedule_pdf
from api.auditoriums_api import create_auditorium, get_auditoriums, get_auditorium, update_auditorium, delete_auditorium
from services.notifications import subscribe_telegram_notification, NOTIFICATIONS_ENABLED
from core.config import LogConfig
from services.calendar_service import generate_calendar_for_user
from services.websocket_manager import manager
from core.logging_config import setup_logging, get_logger

# Инициализируем логирование
setup_logging()
logger = get_logger("main")@asynccontextmanager
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def get_current_user(authorization: Optional[str] = Header(None), access_token: Optional[str] = Cookie(None), db: Session = Depends(get_db)) -> User:
    token = access_token or (authorization.split()[1] if authorization and " " in authorization else None)
    if not token:
        raise HTTPException(status_code=401, detail="Не аутентифицирован")
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Невалидный токен")
    user = get_user_by_id(payload.get("user_id"), db)
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    return user

@app.post("/api/auth/register", response_model=TokenResponse, tags=["🔐 Авторизация"])
async def register(data: RegisterRequest, response: Response, db: Session = Depends(get_db)):
    if get_user_by_email(data.email, db):
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")
    user_id = create_user(data.email, data.password, data.full_name, db)
    token = create_access_token({"user_id": user_id})
    user_info = get_user_by_id(user_id, db)
    set_auth_cookie(response, token)
    return TokenResponse(access_token=token, user=UserResponse.from_orm(user_info))

@app.post("/api/auth/login", response_model=TokenResponse, tags=["🔐 Авторизация"])
async def login(data: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = get_user_by_email(data.email, db)
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Неверные учетные данные")
    token = create_access_token({"user_id": user.id})
    set_auth_cookie(response, token)
    return TokenResponse(access_token=token, user=UserResponse.from_orm(user))

@app.get("/api/auth/me", response_model=UserResponse, tags=["🔐 Авторизация"])
async def get_me(u: User = Depends(get_current_user)):
    return u

@app.post("/api/auth/logout", tags=["🔐 Авторизация"])
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Вы успешно вышли из системы"}

@app.post("/api/auditoriums", response_model=AuditoriumResponse, tags=["🏫 Аудитории"])
async def create_auditorium_ep(data: AuditoriumCreate, u: User = Depends(get_current_user), db: Session = Depends(get_db)):
    auditorium = await create_auditorium(data, db)
    await FastAPICache.clear(namespace="fastapi-cache")
    await manager.broadcast(json.dumps({"type": "auditorium_created", "data": json.loads(AuditoriumResponse.from_orm(auditorium).model_dump_json())}))
    return auditorium

@app.get("/api/auditoriums", response_model=List[AuditoriumResponse], tags=["🏫 Аудитории"])
@cache(expire=60)
async def get_auditoriums_ep(search: Optional[str] = None, db: Session = Depends(get_db)):
    return await get_auditoriums(db, search=search)

@app.get("/api/auditoriums/{auditorium_id}", response_model=AuditoriumResponse, tags=["🏫 Аудитории"])
async def get_auditorium_ep(auditorium_id: int, db: Session = Depends(get_db)):
    return await get_auditorium(auditorium_id, db)

@app.put("/api/auditoriums/{auditorium_id}", response_model=AuditoriumResponse, tags=["🏫 Аудитории"])
async def update_auditorium_ep(auditorium_id: int, data: AuditoriumUpdate, u: User = Depends(get_current_user), db: Session = Depends(get_db)):
    auditorium = await update_auditorium(auditorium_id, data, db)
    await FastAPICache.clear(namespace="fastapi-cache")
    await manager.broadcast(json.dumps({"type": "auditorium_updated", "data": json.loads(AuditoriumResponse.from_orm(auditorium).model_dump_json())}))
    return auditorium

@app.delete("/api/auditoriums/{auditorium_id}", tags=["🏫 Аудитории"])
async def delete_auditorium_ep(auditorium_id: int, u: User = Depends(get_current_user), db: Session = Depends(get_db)):
    await delete_auditorium(auditorium_id, db)
    await FastAPICache.clear(namespace="fastapi-cache")
    await manager.broadcast(json.dumps({"type": "auditorium_deleted", "data": {"id": auditorium_id}}))
    return {"message": "Аудитория успешно удалена"}

@app.post("/api/schedule", response_model=ClassSlotResponse, tags=["🗓️ Расписание"])
async def create_lesson_ep(data: ClassSlotCreate, u: User = Depends(get_current_user), db: Session = Depends(get_db)):
    lesson = await create_class_slot(data, db)
    await manager.broadcast(json.dumps({"type": "lesson_created", "data": json.loads(ClassSlotResponse.from_orm(lesson).model_dump_json())}))
    return lesson

@app.post("/api/schedule/upload", tags=["🗓️ Расписание"])
async def upload_schedule_ep(file: UploadFile = File(...), u: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Загрузка расписания из Excel файла"""
    result = await upload_schedule(db, file)
    await manager.broadcast(json.dumps({"type": "schedule_uploaded", "data": result}))
    return result

@app.get("/api/schedule/export/xlsx", tags=["📥 Экспорт расписания"])
async def export_xlsx_ep(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    single_date: Optional[str] = None,
    group_ids: Optional[List[int]] = None,
    separate_courses: bool = False,
    include_stats: bool = True,
    db: Session = Depends(get_db)
):
    """Экспорт расписания в XLSX формат с расширенным функционалом"""
    return await export_schedule_xlsx(db, date_from, date_to, single_date, group_ids, separate_courses, include_stats)

@app.get("/api/schedule/export/pdf", tags=["📥 Экспорт расписания"])
async def export_pdf_ep(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    single_date: Optional[str] = None,
    group_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Экспорт расписания в PDF формат (оптимизирован для печати)"""
    return await export_schedule_pdf(db, date_from, date_to, single_date, group_id)

@app.get("/api/schedule", response_model=List[dict], tags=["🗓️ Расписание"])
@cache(expire=30)
async def get_schedule_list_ep(date: Optional[str] = None, date_from: Optional[str] = None, date_to: Optional[str] = None, limit: int = 100, offset: int = 0, db: Session = Depends(get_db)):
    return await get_schedule_list(db, date, date_from, date_to, limit, offset)

@app.get("/api/schedule/{lesson_id}", response_model=ClassSlotResponse, tags=["🗓️ Расписание"])
async def get_lesson_ep(lesson_id: int, db: Session = Depends(get_db)):
    return await get_class_slot(lesson_id, db)

@app.put("/api/schedule/{lesson_id}", response_model=ClassSlotResponse, tags=["🗓️ Расписание"])
async def update_lesson_ep(lesson_id: int, data: ClassSlotUpdate, u: User = Depends(get_current_user), db: Session = Depends(get_db)):
    lesson = await update_class_slot(lesson_id, data, db)
    await manager.broadcast(json.dumps({"type": "lesson_updated", "data": json.loads(ClassSlotResponse.from_orm(lesson).model_dump_json())}))
    return lesson

@app.delete("/api/schedule/{lesson_id}", tags=["🗓️ Расписание"])
async def delete_lesson_ep(lesson_id: int, u: User = Depends(get_current_user), db: Session = Depends(get_db)):
    await delete_class_slot(lesson_id, db)
    await manager.broadcast(json.dumps({"type": "lesson_deleted", "data": {"id": lesson_id}}))
    return {"message": "Урок успешно удален"}

@app.get("/api/groups", response_model=List[GroupResponse], tags=["👥 Группы"])
@cache(expire=60)
async def get_groups_ep(name: Optional[str] = None, limit: int = 100, offset: int = 0, db: Session = Depends(get_db)):
    return await get_groups(db, name, limit, offset)

@app.post("/api/groups", response_model=GroupResponse, tags=["👥 Группы"])
async def create_group_ep(data: GroupCreate, u: User = Depends(get_current_user), db: Session = Depends(get_db)):
    group = await create_group(data, db)
    await manager.broadcast(json.dumps({"type": "group_created", "data": json.loads(GroupResponse.from_orm(group).model_dump_json())}))
    return group

@app.get("/api/groups/{group_id}", response_model=GroupResponse, tags=["👥 Группы"])
async def get_group_ep(group_id: int, db: Session = Depends(get_db)):
    return await get_group(group_id, db)

@app.put("/api/groups/{group_id}", response_model=GroupResponse, tags=["👥 Группы"])
async def update_group_ep(group_id: int, data: GroupUpdate, u: User = Depends(get_current_user), db: Session = Depends(get_db)):
    group = await update_group(group_id, data, db)
    await manager.broadcast(json.dumps({"type": "group_updated", "data": json.loads(GroupResponse.from_orm(group).model_dump_json())}))
    return group

@app.delete("/api/groups/{group_id}", tags=["👥 Группы"])
async def delete_group_ep(group_id: int, u: User = Depends(get_current_user), db: Session = Depends(get_db)):
    await delete_group(group_id, db)
    await manager.broadcast(json.dumps({"type": "group_deleted", "data": {"id": group_id}}))
    return {"message": "Группа успешно удалена"}

@app.get("/api/groups/{group_id}/participants", response_model=List[UserResponse], tags=["👥 Участники"])
async def get_group_participants_ep(group_id: int, db: Session = Depends(get_db)):
    return await get_group_participants(group_id, db)

@app.post("/api/groups/{group_id}/participants", tags=["👥 Участники"])
async def add_group_participant_ep(group_id: int, data: AddParticipantRequest, u: User = Depends(get_current_user), db: Session = Depends(get_db)):
    result = await add_participant_to_group(group_id, data.user_id, db)
    await manager.broadcast(json.dumps({"type": "participant_added", "data": {"group_id": group_id, "user_id": data.user_id}}))
    return result

@app.delete("/api/groups/{group_id}/participants/{user_id}", tags=["👥 Участники"])
async def remove_group_participant_ep(group_id: int, user_id: int, u: User = Depends(get_current_user), db: Session = Depends(get_db)):
    await remove_participant_from_group(group_id, user_id, db)
    await manager.broadcast(json.dumps({"type": "participant_removed", "data": {"group_id": group_id, "user_id": user_id}}))
    return {"message": "Участник успешно удален из группы"}

@app.post("/api/notifications/subscribe-telegram", tags=["🔔 Уведомления"])
async def subscribe_telegram_ep(telegram_id: str, u: User = Depends(get_current_user), db: Session = Depends(get_db)):
    u.telegram_id = telegram_id
    db.commit()
    return {"message": "Telegram подписка активирована", "telegram_id": telegram_id}

@app.get("/api/health", tags=["⚙️ Система"])
async def health_check():
    return {"status": "healthy", "telegram": "enabled" if NOTIFICATIONS_ENABLED else "disabled", "database": "connected"}

@app.get("/api/calendar/me.ics", tags=["🗓️ Расписание"])
async def get_my_calendar(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    calendar_content = await generate_calendar_for_user(user.id, db)
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

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
