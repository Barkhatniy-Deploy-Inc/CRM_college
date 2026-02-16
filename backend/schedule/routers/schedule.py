from fastapi import APIRouter, Depends, UploadFile, File
from typing import List, Optional
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import ClassSlotResponse, ClassSlotCreate, ClassSlotUpdate, User
from api.slots_api import create_class_slot, get_class_slot, update_class_slot, delete_class_slot
from api.schedule_api import get_schedule_list, upload_schedule
from dependencies import get_current_user, get_current_active_user
from fastapi_cache.decorator import cache
import json
from services.websocket_manager import manager

# Явный полный путь
router = APIRouter(prefix="/api/schedule", tags=["🗓️ Расписание"])

@router.post("/", response_model=ClassSlotResponse)
async def create_lesson_ep(data: ClassSlotCreate, u: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    lesson = await create_class_slot(data, db)
    await manager.broadcast(json.dumps({"type": "lesson_created", "data": json.loads(ClassSlotResponse.model_validate(lesson).model_dump_json())}))
    return lesson

@router.post("/upload")
async def upload_schedule_ep(file: UploadFile = File(...), u: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Загрузка расписания из Excel файла"""
    result = await upload_schedule(db, file)
    await manager.broadcast(json.dumps({"type": "schedule_uploaded", "data": result}))
    return result

@router.get("/list", response_model=List[dict])
@cache(expire=30)
async def get_schedule_list_ep(date: Optional[str] = None, date_from: Optional[str] = None, date_to: Optional[str] = None, limit: int = 100, offset: int = 0, db: Session = Depends(get_db)):
    return await get_schedule_list(db, date, date_from, date_to, limit, offset)

@router.get("/{lesson_id}", response_model=ClassSlotResponse)
async def get_lesson_ep(lesson_id: int, db: Session = Depends(get_db)):
    return await get_class_slot(lesson_id, db)

@router.put("/{lesson_id}", response_model=ClassSlotResponse)
async def update_lesson_ep(lesson_id: int, data: ClassSlotUpdate, u: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    lesson = await update_class_slot(lesson_id, data, db)
    await manager.broadcast(json.dumps({"type": "lesson_updated", "data": json.loads(ClassSlotResponse.model_validate(lesson).model_dump_json())}))
    return lesson

@router.delete("/{lesson_id}")
async def delete_lesson_ep(lesson_id: int, u: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    await delete_class_slot(lesson_id, db)
    await manager.broadcast(json.dumps({"type": "lesson_deleted", "data": {"id": lesson_id}}))
    return {"message": "Урок успешно удален"}
