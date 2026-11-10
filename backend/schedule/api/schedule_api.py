from fastapi import UploadFile, File, HTTPException
from typing import List, Optional
from datetime import date, datetime, time, timedelta
from sqlalchemy import String
from sqlalchemy.orm import Session, joinedload
from database.models import ClassSlot, Auditorium, Group
from services.schedule_importer import ScheduleImporter
import os
import tempfile
import logging

logger = logging.getLogger(__name__)

async def upload_schedule(db: Session, file: UploadFile = File(...)):
    """
    Загрузка расписания из Excel файла с сохранением в БД.
    
    Процесс:
    1. Проверяет формат файла
    2. Сохраняет временный файл
    3. Парсит файл и сохраняет данные в БД
    4. Возвращает статистику импорта
    """
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=400, 
            detail="File must be Excel (.xlsx or .xls)"
        )

    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_path = temp_file.name

    try:
        # Используем ScheduleImporter для сохранения в БД
        importer = ScheduleImporter(db)
        result = importer.import_schedule(temp_path)
        
        if result['status'] == 'error':
            raise HTTPException(
                status_code=400,
                detail=result['message']
            )
        
        return {
            "status": "success",
            "message": result['message'],
            "groups_created": result['groups_created'],
            "groups_updated": result['groups_updated'],
            "auditoriums_created": result['auditoriums_created'],
            "slots_created": result['slots_created'],
            "slots_updated": result['slots_updated'],
            "errors": result['errors']
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при загрузке расписания: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing schedule file: {str(e)}"
        )
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)

async def get_schedule_list(
        db: Session,
        date: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        group_id: Optional[int] = None,
) -> List[dict]:
    """
    Получение списка занятий с подробной информацией.
    Включает названия группы и аудитории для полноты данных.
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
        Group.name.label("group_name")
    ).outerjoin(Auditorium, ClassSlot.auditorium_id == Auditorium.id).outerjoin(Group, ClassSlot.group_id == Group.id)

    if date_from:
        start_date = _parse_schedule_date(date_from, "date_from")
        query = query.filter(ClassSlot.start_time >= datetime.combine(start_date, time.min))
    if date_to:
        end_date = _parse_schedule_date(date_to, "date_to")
        # date_to is inclusive for callers; use the next midnight as an
        # exclusive upper bound so all times on the final day are included.
        query = query.filter(ClassSlot.start_time < datetime.combine(end_date + timedelta(days=1), time.min))
    if group_id is not None:
        query = query.filter(ClassSlot.group_id == group_id)
    if date and not date_from and not date_to:
        requested_date = _parse_schedule_date(date, "date")
        query = query.filter(
            ClassSlot.start_time >= datetime.combine(requested_date, time.min),
            ClassSlot.start_time < datetime.combine(requested_date + timedelta(days=1), time.min),
        )

    real_limit = 2000 if (date_from or date_to) else limit
    slots = query.order_by(ClassSlot.start_time.desc()).limit(real_limit).offset(offset).all()
    
    return [slot._asdict() for slot in slots]


def _parse_schedule_date(value: str, parameter: str) -> date:
    """Parse an ISO date query parameter and return a client-safe validation error."""
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=f"{parameter} must be an ISO date (YYYY-MM-DD)") from exc
