from fastapi import HTTPException
from schedule.database.database import get_db
from typing import List, Dict
import logging
import sqlite3
from datetime import datetime
from schedule.database.models import UserResponse, ParticipantStatus

logger = logging.getLogger(__name__)


async def get_course_participants(course_id: int) -> List[UserResponse]:
    """Получение участников курса"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM courses WHERE id = ?", (course_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Курс не найден")

        cursor.execute("""
            SELECT DISTINCT u.id, u.email, u.full_name, u.telegram_id
            FROM users u
            JOIN participants p ON u.id = p.user_id
            JOIN class_slots cs ON p.class_slot_id = cs.id
            WHERE cs.course_id = ?
            ORDER BY u.full_name
        """, (course_id,))
        
        rows = cursor.fetchall()
        return [UserResponse.model_validate(row) for row in rows]


async def add_participant_to_course(course_id: int, user_id: int) -> Dict:
    """Добавление существующего участника к курсу с регистрацией на все занятия"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Проверяем, существует ли курс
        cursor.execute("SELECT id FROM courses WHERE id = ?", (course_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Курс не найден")
        
        # Проверяем, существует ли пользователь
        cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        # Находим все занятия (слоты), связанные с этим курсом
        cursor.execute("SELECT id FROM class_slots WHERE course_id = ?", (course_id,))
        slots = cursor.fetchall()
        
        added_count = 0
        if slots:
            now = datetime.now().isoformat()
            for slot in slots:
                try:
                    # Добавляем участника в каждое занятие
                    cursor.execute(
                        "INSERT INTO participants (class_slot_id, user_id, status, registered_at) VALUES (?, ?, ?, ?)",
                        (slot[0], user_id, ParticipantStatus.REGISTERED.value, now)
                    )
                    added_count += 1
                except sqlite3.IntegrityError:
                    # Если участник уже зарегистрирован на это занятие, просто пропускаем
                    pass
        
        conn.commit() # Сохраняем все изменения

        return {
            "message": f"Участник добавлен к {added_count} занятиям курса.",
            "user_id": user_id,
            "slots_added": added_count
        }


async def remove_participant_from_course(course_id: int, user_id: int) -> Dict[str, str]:
    """Удаление участника из всех занятий курса"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM courses WHERE id = ?", (course_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Курс не найден")

        cursor.execute("""
            DELETE FROM participants
            WHERE user_id = ? AND class_slot_id IN (
                SELECT id FROM class_slots WHERE course_id = ?
            )
        """, (user_id, course_id))
        
        deleted_count = cursor.rowcount
        conn.commit() # Сохраняем изменения
        
        if deleted_count == 0:
            raise HTTPException(status_code=404, detail="Участник не найден в этом курсе или уже был удален.")

        return {"message": f"Участник удален с {deleted_count} занятий курса."}
