from fastapi import APIRouter, Depends
from typing import List, Optional
from sqlalchemy.orm import Session
from database.database import get_db
from api.export_api import export_schedule_xlsx, export_schedule_pdf

router = APIRouter(prefix="/export", tags=["📥 Экспорт расписания"])

@router.get("/xlsx")
async def export_xlsx_ep(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    single_date: Optional[str] = None,
    group_ids: Optional[List[int]] = None,
    separate_courses: bool = False,
    include_stats: bool = True,
    db: Session = Depends(get_db)
):
    """Экспорт расписания в XLSX формат с расширенным функционалом"""
    return await export_schedule_xlsx(db, date_from, date_to, single_date, group_ids, separate_courses, include_stats)

@router.get("/pdf")
async def export_pdf_ep(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    single_date: Optional[str] = None,
    group_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Экспорт расписания в PDF формат (оптимизирован для печати)"""
    return await export_schedule_pdf(db, date_from, date_to, single_date, group_id)
