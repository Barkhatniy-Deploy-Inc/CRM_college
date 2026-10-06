from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from database.models import Auditorium, AuditoriumCreate, AuditoriumUpdate, AuditoriumResponse, ClassSlot
from typing import List, Optional
from sqlalchemy.exc import IntegrityError


async def create_auditorium(auditorium: AuditoriumCreate, db: Session) -> AuditoriumResponse:
    """Создание новой аудитории и сохранение в БД."""
    try:
        new_auditorium = Auditorium(**auditorium.model_dump())
        db.add(new_auditorium)
        db.commit()
        db.refresh(new_auditorium)
        return new_auditorium
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Аудитория с названием '{auditorium.name}' уже существует."
        )


async def get_auditoriums(db: Session, search: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[AuditoriumResponse]:
    """Получение списка аудиторий с поиском."""
    query = db.query(Auditorium)
    if search:
        query = query.filter(Auditorium.name.ilike(f"%{search}%"))
    auditoriums = query.offset(offset).limit(limit).all()
    return auditoriums


async def get_auditorium(auditorium_id: int, db: Session) -> AuditoriumResponse:
    """Получение одной аудитории по ID."""
    auditorium = db.query(Auditorium).filter(Auditorium.id == auditorium_id).first()
    if not auditorium:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Аудитория не найдена.")
    return auditorium


async def update_auditorium(auditorium_id: int, auditorium_update: AuditoriumUpdate, db: Session) -> AuditoriumResponse:
    """Обновление данных аудитории."""
    auditorium = await get_auditorium(auditorium_id, db)
    update_data = auditorium_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(auditorium, key, value)
    try:
        db.commit()
        db.refresh(auditorium)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Аудитория с таким названием уже существует."
        )
    return auditorium


async def delete_auditorium(auditorium_id: int, db: Session) -> dict:
    """Удаление аудитории."""
    auditorium = await get_auditorium(auditorium_id, db)
    if db.query(ClassSlot).filter(ClassSlot.auditorium_id == auditorium_id).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Нельзя удалить аудиторию, так как она используется в расписании."
        )
    db.delete(auditorium)
    db.commit()
    return {"message": "Аудитория успешно удалена."}
