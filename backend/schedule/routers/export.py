from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from database.database import get_db
from api.export_api import export_schedule_xlsx, export_schedule_pdf

router = APIRouter(prefix="/api/schedule/export", tags=["📥 Экспорт расписания"])

@router.get("/xlsx")
async def export_xlsx_ep(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    single_date: Optional[str] = None,
    group_ids: Optional[List[int]] = Query(None),
    separate_courses: bool = False,
    include_stats: bool = True,
    instructor: Optional[str] = None,
    auditorium_ids: Optional[List[int]] = Query(None),
    title_search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Экспорт расписания в XLSX формат с расширенным функционалом"""
    return await export_schedule_xlsx(
        db,
        date_from,
        date_to,
        single_date,
        group_ids,
        separate_courses,
        include_stats,
        instructor,
        auditorium_ids,
        title_search,
    )

@router.get("/pdf")
async def export_pdf_ep(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    single_date: Optional[str] = None,
    group_id: Optional[int] = None,
    instructor: Optional[str] = None,
    auditorium_ids: Optional[List[int]] = Query(None),
    title_search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Экспорт расписания в PDF формат (оптимизирован для печати)"""
    return await export_schedule_pdf(
        db,
        date_from,
        date_to,
        single_date,
        group_id,
        instructor,
        auditorium_ids,
        title_search,
    )
