from fastapi import HTTPException, status
from schedule.database.database import get_db
from schedule.database.models import AuditoriumCreate, AuditoriumUpdate, AuditoriumResponse
from typing import List, Optional
import sqlite3


async def create_auditorium(auditorium: AuditoriumCreate) -> AuditoriumResponse:
    """Создание новой аудитории и сохранение в БД."""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO auditoriums (name, capacity, description) VALUES (?, ?, ?)",
                (auditorium.name, auditorium.capacity, auditorium.description)
            )
            new_id = cursor.lastrowid

        return AuditoriumResponse(id=new_id, **auditorium.model_dump())
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Аудитория с названием '{auditorium.name}' уже существует."
        )


async def get_auditoriums(search: Optional[str] = None, limit: int = 100) -> List[AuditoriumResponse]:
    """Получение списка аудиторий с поиском."""
    with get_db() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM auditoriums"
        params = []

        if search:
            query += " WHERE name LIKE ?"
            params.append(f"%{search}%")

        query += " ORDER BY name LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()

        return [AuditoriumResponse.model_validate(dict(row)) for row in rows]


async def get_auditorium(auditorium_id: int) -> AuditoriumResponse:
    """Получение одной аудитории по ID."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM auditoriums WHERE id = ?", (auditorium_id,))
        row = cursor.fetchone()

        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Аудитория не найдена.")

        return AuditoriumResponse.model_validate(dict(row))


async def update_auditorium(auditorium_id: int, auditorium: AuditoriumUpdate) -> AuditoriumResponse:
    """Обновление данных аудитории."""
    update_data = auditorium.model_dump(exclude_unset=True)
    if not update_data:
        return await get_auditorium(auditorium_id)

    with get_db() as conn:
        cursor = conn.cursor()

        # Получаем текущие данные
        current_auditorium = await get_auditorium(auditorium_id)
        updated_auditorium_data = current_auditorium.model_dump()
        updated_auditorium_data.update(update_data)
        updated_auditorium = AuditoriumResponse(**updated_auditorium_data)

        # Обновляем в БД
        set_clause = ", ".join([f"{key} = ?" for key in update_data])
        query = f"UPDATE auditoriums SET {set_clause} WHERE id = ?"
        params = list(update_data.values()) + [auditorium_id]

        try:
            cursor.execute(query, params)
            if cursor.rowcount == 0:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Аудитория не найдена.")
        except sqlite3.IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Аудитория с таким названием уже существует."
            )

    return updated_auditorium


async def delete_auditorium(auditorium_id: int) -> dict:
    """Удаление аудитории."""
    with get_db() as conn:
        cursor = conn.cursor()

        # Проверяем, используется ли аудитория
        cursor.execute("SELECT id FROM class_slots WHERE auditorium_id = ?", (auditorium_id,))
        if cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Нельзя удалить аудиторию, так как она используется в расписании."
            )

        # Удаляем
        cursor.execute("DELETE FROM auditoriums WHERE id = ?", (auditorium_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Аудитория не найдена.")

    return {"message": "Аудитория успешно удалена."}
