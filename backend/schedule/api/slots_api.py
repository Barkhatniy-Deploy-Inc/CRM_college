from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import ClassSlot, ClassSlotCreate, ClassSlotUpdate, ClassSlotResponse, SlotStatus, Course, Auditorium
from typing import Optional, List, Dict
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


async def is_auditorium_available(auditorium_id: int, start_time: datetime, end_time: datetime, db: Session, ignore_slot_id: Optional[int] = None) -> bool:
    """Проверяет, свободна ли аудитория в указанный временной промежуток."""
    query = db.query(ClassSlot).filter(
        ClassSlot.auditorium_id == auditorium_id,
        ClassSlot.start_time < end_time,
        ClassSlot.end_time > start_time
    )
    if ignore_slot_id:
        query = query.filter(ClassSlot.id != ignore_slot_id)
    return query.first() is None


async def create_class_slot(data: ClassSlotCreate, db: Session = Depends(get_db)) -> ClassSlotResponse:
    """Создание нового урока с проверкой доступности аудитории."""
    if not db.query(Course).filter(Course.id == data.course_id).first():
        raise HTTPException(status_code=404, detail=f"Курс с ID {data.course_id} не найден")

    if data.auditorium_id:
        if not await is_auditorium_available(data.auditorium_id, data.start_time, data.end_time, db):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Аудитория занята в это время."
            )
    
    new_slot = ClassSlot(**data.model_dump())
    db.add(new_slot)
    db.commit()
    db.refresh(new_slot)
    return new_slot


async def get_class_slot(slot_id: int, db: Session = Depends(get_db)) -> ClassSlotResponse:
    """Получение урока по ID."""
    slot = db.query(ClassSlot).filter(ClassSlot.id == slot_id).first()
    if not slot:
        raise HTTPException(status_code=404, detail=f"Урок с ID {slot_id} не найден")
    return slot


async def update_class_slot(slot_id: int, data: ClassSlotUpdate, db: Session = Depends(get_db)) -> ClassSlotResponse:
    """Обновление урока с проверкой доступности аудитории."""
    slot = await get_class_slot(slot_id, db)
    update_data = data.model_dump(exclude_unset=True)

    if 'auditorium_id' in update_data or 'start_time' in update_data or 'end_time' in update_data:
        auditorium_id = update_data.get('auditorium_id', slot.auditorium_id)
        start_time = update_data.get('start_time', slot.start_time)
        end_time = update_data.get('end_time', slot.end_time)

        if auditorium_id and not await is_auditorium_available(auditorium_id, start_time, end_time, db, ignore_slot_id=slot_id):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Аудитория занята в это время.")

    for key, value in update_data.items():
        setattr(slot, key, value)
    
    db.commit()
    db.refresh(slot)
    return slot


async def delete_class_slot(slot_id: int, db: Session = Depends(get_db)) -> Dict[str, str]:
    """Удаление урока."""
    slot = await get_class_slot(slot_id, db)
    db.delete(slot)
    db.commit()
    return {"message": f"Урок {slot_id} успешно удалён"}
