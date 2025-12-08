from fastapi import UploadFile, File, HTTPException, Depends
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from database.database import get_db
from database.models import ClassSlot, Auditorium, Course
from core.parser import parse_excel_schedule
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
        offset: int = 0,
        db: Session = Depends(get_db)
) -> List[dict]:
    """
    Получение списка занятий с подробной информацией.
    Включает названия курса и аудитории для полноты данных.
    """
    query = db.query(
        ClassSlot.id,
        ClassSlot.title,
        ClassSlot.start_time,
        ClassSlot.end_time,
        ClassSlot.auditorium_id,
        ClassSlot.instructor.label("teacher_name"),
        ClassSlot.status,
        Auditorium.name.label("auditorium_name"),
        Course.name.label("course_name")
    ).outerjoin(Auditorium, ClassSlot.auditorium_id == Auditorium.id).outerjoin(Course, ClassSlot.course_id == Course.id)

    if date_from and date_to:
        query = query.filter(ClassSlot.start_time.between(date_from, date_to))
    elif date:
        query = query.filter(ClassSlot.start_time.like(f"{date}%"))

    real_limit = 2000 if (date_from or date_to) else limit
    slots = query.order_by(ClassSlot.start_time.desc()).limit(real_limit).offset(offset).all()
    
    return [slot._asdict() for slot in slots]
