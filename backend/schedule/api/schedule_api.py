from fastapi import UploadFile, File, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from schedule.database.database import get_db
from schedule.core.parser import parse_excel_schedule
import os
import tempfile

async def upload_schedule(file: UploadFile = File(...)):
    """Загрузка расписания из Excel файла"""
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="File must be Excel (.xlsx or .xls)")

    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_path = temp_file.name

    try:
        entries = parse_excel_schedule(temp_path)
        # Логика сохранения в БД была бы здесь
        return {
            "message": "Schedule uploaded successfully",
            "entries_count": len(entries)
        }
    finally:
        os.unlink(temp_path)

async def get_schedule_list(
        date: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
) -> List[dict]:
    """
    Получение списка занятий с подробной информацией.
    Включает названия курса и аудитории для полноты данных.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        # Расширяем запрос, чтобы получать названия курса и аудитории
        query = """
            SELECT
                cs.id,
                cs.title,
                cs.start_time,
                cs.end_time,
                cs.auditorium_id,
                cs.instructor as teacher_name, -- Алиас для консистентности с другими частями системы
                cs.status,
                a.name as auditorium_name,
                c.name as course_name
            FROM class_slots cs
            LEFT JOIN auditoriums a ON cs.auditorium_id = a.id
            LEFT JOIN courses c ON cs.course_id = c.id
            WHERE 1=1
        """
        params = []

        if date_from and date_to:
            query += " AND date(cs.start_time) >= ? AND date(cs.start_time) <= ?"
            params.extend([date_from, date_to])
        elif date:
            query += " AND date(cs.start_time) = ?"
            params.append(date)

        # Лимит по умолчанию для запросов без диапазона дат
        real_limit = 2000 if (date_from or date_to) else limit
        query += " ORDER BY cs.start_time DESC LIMIT ? OFFSET ?"
        params.extend([real_limit, offset])

        cursor.execute(query, params)
        rows = cursor.fetchall()

        # Преобразуем строки из БД в словари
        return [dict(row) for row in rows]
