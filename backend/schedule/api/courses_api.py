from fastapi import HTTPException, status
from schedule.database.database import get_db
from schedule.database.models import CourseCreate, CourseUpdate, CourseResponse
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


async def create_course(data: CourseCreate) -> CourseResponse:
    """Создание нового курса."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO courses (name, description, instructor) VALUES (?, ?, ?)",
            (data.name, data.description, data.instructor)
        )
        new_id = cursor.lastrowid
        return CourseResponse(id=new_id, **data.model_dump())


async def get_courses(name: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[CourseResponse]:
    """Получение списка курсов с фильтрацией."""
    with get_db() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM courses WHERE 1=1"
        params = []
        if name:
            query += " AND name LIKE ?"
            params.append(f"%{name}%")
        query += " ORDER BY name LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [CourseResponse.model_validate(dict(row)) for row in rows]


async def get_course(course_id: int) -> CourseResponse:
    """Получение одного курса по ID."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM courses WHERE id = ?", (course_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Курс не найден.")
        return CourseResponse.model_validate(dict(row))


async def update_course(course_id: int, data: CourseUpdate) -> CourseResponse:
    """Обновление курса."""
    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Нет данных для обновления.")
    
    with get_db() as conn:
        cursor = conn.cursor()
        query = f"UPDATE courses SET {', '.join([f'{key} = ?' for key in update_data])} WHERE id = ?"
        params = list(update_data.values()) + [course_id]
        cursor.execute(query, params)
        if cursor.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Курс не найден.")
        return await get_course(course_id)


async def delete_course(course_id: int) -> dict:
    """Удаление курса."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM courses WHERE id = ?", (course_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Курс не найден.")
        return {"message": "Курс успешно удален."}
