from fastapi import HTTPException, status
from schedule.database.database import get_db
from schedule.database.models import ClassSlotCreate, ClassSlotUpdate, ClassSlotResponse, SlotStatus
from typing import Optional, List, Dict
import logging
from datetime import datetime

# Импорт уведомлений
try:
    from services.notifications import notify_slot_created, notify_slot_status_changed, NOTIFICATIONS_ENABLED
except ImportError:
    NOTIFICATIONS_ENABLED = False
    async def notify_slot_created(*args, **kwargs): return {"success_count": 0, "failed_count": 0}
    async def notify_slot_status_changed(*args, **kwargs): return {"success_count": 0, "failed_count": 0}

logger = logging.getLogger(__name__)


async def is_auditorium_available(auditorium_id: int, start_time: datetime, end_time: datetime, conn, ignore_slot_id: Optional[int] = None) -> bool:
    """Проверяет, свободна ли аудитория в указанный временной промежуток."""
    cursor = conn.cursor()
    query = """
        SELECT id FROM class_slots
        WHERE auditorium_id = ?
        AND (start_time < ? AND end_time > ?)
    """
    params = [auditorium_id, end_time.isoformat(), start_time.isoformat()]
    
    if ignore_slot_id:
        query += " AND id != ?"
        params.append(ignore_slot_id)
        
    cursor.execute(query, params)
    return cursor.fetchone() is None


async def create_class_slot(data: ClassSlotCreate) -> ClassSlotResponse:
    """Создание нового урока с проверкой доступности аудитории."""
    with get_db() as conn:
        cursor = conn.cursor()

        # Проверка курса
        cursor.execute("SELECT id FROM courses WHERE id = ?", (data.course_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail=f"Курс с ID {data.course_id} не найден")

        # Проверка доступности аудитории
        if data.auditorium_id:
            if not await is_auditorium_available(data.auditorium_id, data.start_time, data.end_time, conn):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Аудитория занята в это время."
                )
        
        # Вставка данных
        cursor.execute("""
            INSERT INTO class_slots (course_id, auditorium_id, title, start_time, end_time, instructor, max_participants, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.course_id, data.auditorium_id, data.title, data.start_time.isoformat(), data.end_time.isoformat(),
            data.instructor, data.max_participants, data.status.value
        ))
        slot_id = cursor.lastrowid
        logger.info(f"✅ Создан урок ID={slot_id} в БД")
        
        # Собираем ответ вручную, не вызывая get_class_slot
        response_data = data.model_dump()
        response_data['id'] = slot_id
        
        return ClassSlotResponse.model_validate(response_data)


async def get_class_slot(slot_id: int) -> ClassSlotResponse:
    """Получение урока по ID."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM class_slots WHERE id = ?", (slot_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail=f"Урок с ID {slot_id} не найден")
        return ClassSlotResponse.model_validate(dict(row))


async def update_class_slot(slot_id: int, data: ClassSlotUpdate) -> ClassSlotResponse:
    """Обновление урока с проверкой доступности аудитории."""
    with get_db() as conn:
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return await get_class_slot(slot_id)

        # Проверка доступности, если меняется время или аудитория
        if 'auditorium_id' in update_data or 'start_time' in update_data or 'end_time' in update_data:
            cursor = conn.cursor()
            cursor.execute("SELECT auditorium_id, start_time, end_time FROM class_slots WHERE id = ?", (slot_id,))
            current_slot = cursor.fetchone()
            if not current_slot:
                raise HTTPException(status_code=404, detail="Урок не найден.")

            auditorium_id = update_data.get('auditorium_id', current_slot['auditorium_id'])
            start_time = update_data.get('start_time', datetime.fromisoformat(current_slot['start_time']))
            end_time = update_data.get('end_time', datetime.fromisoformat(current_slot['end_time']))

            if auditorium_id and not await is_auditorium_available(auditorium_id, start_time, end_time, conn, ignore_slot_id=slot_id):
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Аудитория занята в это время.")

        for key, value in update_data.items():
            if isinstance(value, (datetime, SlotStatus)):
                update_data[key] = value.isoformat() if isinstance(value, datetime) else value.value
        
        query = f"UPDATE class_slots SET {', '.join([f'{key} = ?' for key in update_data])} WHERE id = ?"
        params = list(update_data.values()) + [slot_id]
        conn.cursor().execute(query, params)
        
    return await get_class_slot(slot_id)


async def delete_class_slot(slot_id: int) -> Dict[str, str]:
    """Удаление урока."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM class_slots WHERE id = ?", (slot_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"Урок с ID {slot_id} не найден")
        return {"message": f"Урок {slot_id} успешно удалён"}
