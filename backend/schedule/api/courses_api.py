from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import Course, CourseCreate, CourseUpdate, CourseResponse
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


async def create_course(data: CourseCreate, db: Session = Depends(get_db)) -> CourseResponse:
    """Создание нового курса."""
    new_course = Course(**data.model_dump())
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course


async def get_courses(name: Optional[str] = None, limit: int = 100, offset: int = 0, db: Session = Depends(get_db)) -> List[CourseResponse]:
    """Получение списка курсов с фильтрацией."""
    query = db.query(Course)
    if name:
        query = query.filter(Course.name.ilike(f"%{name}%"))
    courses = query.offset(offset).limit(limit).all()
    return courses


async def get_course(course_id: int, db: Session = Depends(get_db)) -> CourseResponse:
    """Получение одного курса по ID."""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Курс не найден.")
    return course


async def update_course(course_id: int, data: CourseUpdate, db: Session = Depends(get_db)) -> CourseResponse:
    """Обновление курса."""
    course = await get_course(course_id, db)
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(course, key, value)
    db.commit()
    db.refresh(course)
    return course


async def delete_course(course_id: int, db: Session = Depends(get_db)) -> dict:
    """Удаление курса."""
    course = await get_course(course_id, db)
    db.delete(course)
    db.commit()
    return {"message": "Курс успешно удален."}
