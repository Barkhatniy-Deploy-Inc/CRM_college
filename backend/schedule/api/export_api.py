"""
API endpoints для экспорта расписания в XLSX и PDF форматы.
"""

from fastapi import HTTPException
from typing import Optional, List
from sqlalchemy.orm import Session
from services.schedule_exporter import ScheduleExporter
from fastapi.responses import StreamingResponse
import logging
from datetime import datetime
from urllib.parse import quote
from core.logging_config import get_logger

logger = get_logger("export_api")


def _content_disposition(filename: str) -> str:
    """Формирует безопасный заголовок Content-Disposition.

    HTTP-заголовки кодируются в latin-1, поэтому кириллицу в filename
    передаём через RFC 5987 (filename*), оставляя ASCII-fallback.
    """
    ext = ""
    if "." in filename:
        ext = "." + filename.rsplit(".", 1)[1]
    ascii_fallback = f"schedule_export{ext}"
    return f"attachment; filename={ascii_fallback}; filename*=UTF-8''{quote(filename)}"


async def export_schedule_xlsx(
    db: Session,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    single_date: Optional[str] = None,
    group_ids: Optional[List[int]] = None,
    separate_courses: bool = False,
    include_stats: bool = True,
    instructor: Optional[str] = None,
    auditorium_ids: Optional[List[int]] = None,
    title_search: Optional[str] = None
):
    """
    Экспорт расписания в XLSX формат с поддержкой расширенной фильтрации.
    
    **Параметры:**
    - `date_from`, `date_to`: диапазон дат (формат ДД.MM.YYYY)
    - `single_date`: конкретная дата (формат ДД.MM.YYYY)
    - `group_ids`: список ID групп для экспорта (если не указаны, экспортируются все)
    - `separate_courses`: если True, каждый курс будет на отдельном листе
    - `include_stats`: если True, добавляется лист со статистикой
    - `instructor`: фильтр по преподавателю (частичное совпадение, case-insensitive)
    - `auditorium_ids`: список ID аудиторий для фильтрации
    - `title_search`: поиск по названию предмета (частичное совпадение, case-insensitive)
    
    **Примеры:**
    - `/api/schedule/export/xlsx?date_from=01.09.2025&date_to=06.09.2025&separate_courses=true`
    - `/api/schedule/export/xlsx?single_date=03.09.2025&instructor=Иванов`
    - `/api/schedule/export/xlsx?title_search=математика&separate_courses=true`
    - `/api/schedule/export/xlsx?auditorium_ids=1&auditorium_ids=2&instructor=Петров`
    """
    try:
        # Валидация дат
        if date_from and date_to:
            try:
                datetime.strptime(date_from, "%d.%m.%Y")
                datetime.strptime(date_to, "%d.%m.%Y")
            except ValueError:
                raise HTTPException(status_code=400, detail="Неверный формат даты (используйте ДД.MM.YYYY)")

        if single_date:
            try:
                datetime.strptime(single_date, "%d.%m.%Y")
            except ValueError:
                raise HTTPException(status_code=400, detail="Неверный формат даты (используйте ДД.MM.YYYY)")

        logger.info("📊 API запрос: экспорт XLSX")
        logger.info(f"   Параметры: date_from={date_from}, date_to={date_to}, single_date={single_date}")
        logger.info(f"   Фильтры: instructor={instructor}, title={title_search}, auditorium_ids={auditorium_ids}")

        exporter = ScheduleExporter(db)
        excel_file = exporter.export_to_xlsx(
            date_from=date_from,
            date_to=date_to,
            single_date=single_date,
            group_ids=group_ids,
            separate_courses=separate_courses,
            include_stats=include_stats,
            instructor=instructor,
            auditorium_ids=auditorium_ids,
            title_search=title_search
        )

        # Определяем имя файла
        if single_date:
            filename = f"расписание_{single_date}.xlsx"
        elif date_from and date_to:
            filename = f"расписание_{date_from}_до_{date_to}.xlsx"
        else:
            filename = "расписание.xlsx"

        logger.info(f"✅ XLSX файл готов: {filename}")
        return StreamingResponse(
            iter([excel_file.getvalue()]),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": _content_disposition(filename)}
        )

    except HTTPException:
        logger.warning(f"❌ Ошибка валидации при экспорте XLSX")
        raise
    except Exception as e:
        logger.error(f"❌ Критическая ошибка при экспорте XLSX: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ошибка при экспорте: {str(e)}")


async def export_schedule_pdf(
    db: Session,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    single_date: Optional[str] = None,
    group_id: Optional[int] = None,
    instructor: Optional[str] = None,
    auditorium_ids: Optional[List[int]] = None,
    title_search: Optional[str] = None
):
    """
    Экспорт расписания в PDF формат (оптимизирован для печати) с поддержкой расширенной фильтрации.
    
    **Параметры:**
    - `date_from`, `date_to`: диапазон дат (формат ДД.MM.YYYY)
    - `single_date`: конкретная дата (формат ДД.MM.YYYY)
    - `group_id`: если указан, экспортируется расписание конкретной группы.
                  Если не указан, экспортируются все курсы (по отдельным страницам)
    - `instructor`: фильтр по преподавателю (частичное совпадение, case-insensitive)
    - `auditorium_ids`: список ID аудиторий для фильтрации
    - `title_search`: поиск по названию предмета (частичное совпадение, case-insensitive)
    
    **Примеры:**
    - `/api/schedule/export/pdf?single_date=03.09.2025` (все курсы на дату)
    - `/api/schedule/export/pdf?group_id=5` (расписание группы с ID 5)
    - `/api/schedule/export/pdf?date_from=01.09.2025&date_to=06.09.2025&instructor=Иванов`
    - `/api/schedule/export/pdf?title_search=физика&auditorium_ids=1&auditorium_ids=2`
    """
    try:
        # Валидация дат
        if date_from and date_to:
            try:
                datetime.strptime(date_from, "%d.%m.%Y")
                datetime.strptime(date_to, "%d.%m.%Y")
            except ValueError:
                raise HTTPException(status_code=400, detail="Неверный формат даты (используйте ДД.MM.YYYY)")

        if single_date:
            try:
                datetime.strptime(single_date, "%d.%m.%Y")
            except ValueError:
                raise HTTPException(status_code=400, detail="Неверный формат даты (используйте ДД.MM.YYYY)")

        logger.info("📊 API запрос: экспорт PDF")
        logger.info(f"   Параметры: date_from={date_from}, date_to={date_to}, single_date={single_date}, group_id={group_id}")
        logger.info(f"   Фильтры: instructor={instructor}, title={title_search}, auditorium_ids={auditorium_ids}")

        exporter = ScheduleExporter(db)
        pdf_file = exporter.export_to_pdf(
            date_from=date_from,
            date_to=date_to,
            single_date=single_date,
            group_id=group_id,
            instructor=instructor,
            auditorium_ids=auditorium_ids,
            title_search=title_search
        )

        # Определяем имя файла
        if group_id:
            filename = f"расписание_группа_{group_id}.pdf"
        elif single_date:
            filename = f"расписание_{single_date}.pdf"
        elif date_from and date_to:
            filename = f"расписание_{date_from}_до_{date_to}.pdf"
        else:
            filename = "расписание.pdf"

        logger.info(f"✅ PDF файл готов: {filename}")
        return StreamingResponse(
            iter([pdf_file.getvalue()]),
            media_type="application/pdf",
            headers={"Content-Disposition": _content_disposition(filename)}
        )

    except HTTPException:
        logger.warning(f"❌ Ошибка валидации при экспорте PDF")
        raise
    except Exception as e:
        logger.error(f"❌ Критическая ошибка при экспорте PDF: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ошибка при экспорте: {str(e)}")
