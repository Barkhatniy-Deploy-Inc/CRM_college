from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from database.models import Group, GroupCreate, GroupUpdate, GroupResponse
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


async def create_group(data: GroupCreate, db: Session) -> GroupResponse:
    """Создание новой группы."""
    new_group = Group(**data.model_dump())
    db.add(new_group)
    db.commit()
    db.refresh(new_group)
    return new_group


async def get_groups(db: Session, name: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[GroupResponse]:
    """Получение списка групп с фильтрацией."""
    query = db.query(Group)
    if name:
        query = query.filter(Group.name.ilike(f"%{name}%"))
    groups = query.offset(offset).limit(limit).all()
    return groups


async def get_group(group_id: int, db: Session) -> GroupResponse:
    """Получение одной группы по ID."""
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Группа не найдена.")
    return group


async def update_group(group_id: int, data: GroupUpdate, db: Session) -> GroupResponse:
    """Обновление группы."""
    group = await get_group(group_id, db)
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(group, key, value)
    db.commit()
    db.refresh(group)
    return group


async def delete_group(group_id: int, db: Session) -> dict:
    """Удаление группы."""
    group = await get_group(group_id, db)
    db.delete(group)
    db.commit()
    return {"message": "Группа успешно удалена."}
