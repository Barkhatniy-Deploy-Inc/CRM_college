"""
Сервис экспорта расписания в XLSX и PDF форматы.
Поддерживает гибкую настройку: диапазон дат, разделение курсов, форматирование.
"""

from typing import Optional, List, Dict, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database.models import ClassSlot, Group, Auditorium
from io import BytesIO
import logging

# XLSX экспорт
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# PDF экспорт
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm, inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor

logger = logging.getLogger(__name__)

# Цвета для курсов
COURSE_COLORS = {
    1: "FFE6E6",  # Красный
    2: "E6F3FF",  # Синий
    3: "E6FFE6",  # Зелёный
    4: "FFF3E6",  # Оранжевый
}

DAY_NAMES = {
    0: "Пн",
    1: "Вт",
    2: "Ср",
    3: "Чт",
    4: "Пт",
    5: "Сб",
    6: "Вс"
}


class ScheduleExporter:
    """Экспортер расписания в XLSX и PDF"""

    def __init__(self, db: Session):
        self.db = db
        logger.info("✨ Инициализирован ScheduleExporter")

    def get_date_range(
        self,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        single_date: Optional[str] = None
    ) -> Tuple[datetime, datetime]:
        """Получить диапазон дат для экспорта"""
        if single_date:
            dt = datetime.strptime(single_date, "%d.%m.%Y")
            logger.debug(f"📅 Конкретная дата: {single_date}")
            return dt.replace(hour=0, minute=0, second=0), dt.replace(hour=23, minute=59, second=59)

        if date_from and date_to:
            from_dt = datetime.strptime(date_from, "%d.%m.%Y")
            to_dt = datetime.strptime(date_to, "%d.%m.%Y")
            logger.debug(f"📅 Диапазон дат: {date_from} - {date_to}")
            return from_dt.replace(hour=0, minute=0), to_dt.replace(hour=23, minute=59)

        # По умолчанию неделя
        today = datetime.now()
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
        logger.debug(f"📅 Используется текущая неделя: {start.strftime('%d.%m')} - {end.strftime('%d.%m')}")

    def get_slots_by_group(
        self,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        single_date: Optional[str] = None,
        group_ids: Optional[List[int]] = None,
        instructor: Optional[str] = None,
        auditorium_ids: Optional[List[int]] = None,
        title_search: Optional[str] = None
    ) -> Dict[int, List[ClassSlot]]:
        """Получить занятия, сгруппированные по группам с фильтрацией"""
        start, end = self.get_date_range(date_from, date_to, single_date)

        query = self.db.query(ClassSlot).filter(
            ClassSlot.start_time >= start,
            ClassSlot.start_time <= end
        ).order_by(ClassSlot.start_time)

        logger.info(f"🔍 Начало поиска занятий с параметрами:")
        logger.info(f"   - Дата: {start.strftime('%d.%m.%Y')} - {end.strftime('%d.%m.%Y')}")

        if group_ids:
            query = query.filter(ClassSlot.group_id.in_(group_ids))
            logger.info(f"   - Группы: {group_ids}")

        if instructor:
            query = query.filter(ClassSlot.instructor.ilike(f"%{instructor}%"))
            logger.info(f"   - Преподаватель: {instructor}")

        if auditorium_ids:
            query = query.filter(ClassSlot.auditorium_id.in_(auditorium_ids))
            logger.info(f"   - Аудитории: {auditorium_ids}")

        if title_search:
            query = query.filter(ClassSlot.title.ilike(f"%{title_search}%"))
            logger.info(f"   - Предмет: {title_search}")

        slots = query.all()
        logger.info(f"✅ Найдено {len(slots)} занятий")

        # Группировка по group_id
        result = {}
        for slot in slots:
            if slot.group_id not in result:
                result[slot.group_id] = []
            result[slot.group_id].append(slot)

        logger.info(f"📊 Распределено по {len(result)} группам")
        return result

    def export_to_xlsx(
        self,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        single_date: Optional[str] = None,
        group_ids: Optional[List[int]] = None,
        separate_courses: bool = False,
        include_stats: bool = True,
        instructor: Optional[str] = None,
        auditorium_ids: Optional[List[int]] = None,
        title_search: Optional[str] = None
    ) -> BytesIO:
        """
        Экспорт расписания в XLSX формат с расширенным функционалом.
        
        Args:
            date_from: Дата начала (ДД.MM.YYYY)
            date_to: Дата конца (ДД.MM.YYYY)
            single_date: Конкретная дата (ДД.MM.YYYY)
            group_ids: Список ID групп (None = все)
            separate_courses: Разделить курсы по листам
            include_stats: Включить статистику
            instructor: Фильтр по преподавателю (поиск по частичному совпадению)
            auditorium_ids: Список ID аудиторий
            title_search: Фильтр по названию предмета (поиск по частичному совпадению)
        """
        logger.info("=" * 60)
        logger.info("🚀 НАЧАЛО ЭКСПОРТА В XLSX")
        logger.info("=" * 60)

        slots_by_group = self.get_slots_by_group(
            date_from=date_from,
            date_to=date_to,
            single_date=single_date,
            group_ids=group_ids,
            instructor=instructor,
            auditorium_ids=auditorium_ids,
            title_search=title_search
        )

        if not slots_by_group:
            logger.warning("⚠️  По указанным фильтрам не найдено занятий")
            return BytesIO()

        wb = openpyxl.Workbook()
        wb.remove(wb.active)  # Удалить пустой лист

        # Определяем курсы
        groups = self.db.query(Group).all()
        group_by_id = {g.id: g for g in groups}

        if separate_courses:
            logger.info("📝 Режим экспорта: разделение по курсам")
            # По одному листу на курс
            courses = self._extract_courses(slots_by_group, group_by_id)
            for course, group_ids_in_course in courses.items():
                ws = wb.create_sheet(f"Курс {course}")
                logger.debug(f"📄 Создан лист 'Курс {course}' с {len(group_ids_in_course)} группами")
                self._fill_sheet(ws, slots_by_group, group_ids_in_course, group_by_id)
        else:
            logger.info("📝 Режим экспорта: все в одном листе")
            # Все в одном листе
            ws = wb.create_sheet("Расписание")
            all_group_ids = list(slots_by_group.keys())
            logger.debug(f"📄 Создан лист 'Расписание' с {len(all_group_ids)} группами")
            self._fill_sheet(ws, slots_by_group, all_group_ids, group_by_id)

        # Лист со статистикой
        if include_stats:
            logger.info("📊 Добавляется лист со статистикой")
            self._add_stats_sheet(wb, slots_by_group, group_by_id)

        # Сохранить в BytesIO
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        logger.info("✅ ЭКСПОРТ В XLSX ЗАВЕРШЁН УСПЕШНО")
        logger.info("=" * 60)
        return output

    def _extract_courses(self, slots_by_group: Dict, group_by_id: Dict) -> Dict[int, List[int]]:
        """Извлечь курсы из групп"""
        courses = {}
        for group_id in slots_by_group.keys():
            group = group_by_id.get(group_id)
            if group:
                # Парсим курс из названия группы (например "СД-25/9-П" = 2 курс)
                course = self._extract_course_number(group.name)
                if course not in courses:
                    courses[course] = []
                courses[course].append(group_id)
        return dict(sorted(courses.items()))

    def _extract_course_number(self, group_name: str) -> int:
        """Извлечь номер курса из названия группы"""
        try:
            # Формат: "АБ-25/9-П", курс это вторая цифра после slash
            parts = group_name.split("/")
            if len(parts) >= 2:
                return int(parts[1][0])
        except:
            pass
        return 1

    def _fill_sheet(self, ws, slots_by_group: Dict, group_ids: List[int], group_by_id: Dict):
        """Заполнить лист расписанием"""
        ws.column_dimensions['A'].width = 15
        ws.column_dimensions['B'].width = 12
        ws.column_dimensions['C'].width = 12
        ws.column_dimensions['D'].width = 30
        ws.column_dimensions['E'].width = 18
        ws.column_dimensions['F'].width = 12

        # Заголовок
        headers = ["Группа", "День", "Время", "Предмет", "Преподаватель", "Аудитория"]
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF", size=11)
        header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = header_alignment

        ws.row_dimensions[1].height = 25

        # Данные
        row = 2
        thin_border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )

        for group_id in sorted(group_ids):
            if group_id not in slots_by_group:
                continue

            slots = slots_by_group[group_id]
            group = group_by_id.get(group_id)
            group_name = group.name if group else f"Group {group_id}"

            # Определяем курс для цвета
            course = self._extract_course_number(group_name)
            fill_color = COURSE_COLORS.get(course, "FFFFFF")
            fill = PatternFill(start_color=fill_color, end_color=fill_color, fill_type="solid")

            # Сортируем по дате и времени
            slots = sorted(slots, key=lambda s: s.start_time)

            for slot in slots:
                ws.cell(row=row, column=1, value=group_name)
                ws.cell(row=row, column=2, value=f"{slot.start_time.strftime('%d.%m')} ({DAY_NAMES[slot.start_time.weekday()]})")
                ws.cell(row=row, column=3, value=slot.start_time.strftime('%H:%M-%I:%M'))  # TODO: Исправить формат времени
                ws.cell(row=row, column=4, value=slot.title)
                ws.cell(row=row, column=5, value=slot.instructor or "-")

                auditorium = self.db.query(Auditorium).filter(Auditorium.id == slot.auditorium_id).first()
                ws.cell(row=row, column=6, value=auditorium.name if auditorium else "-")

                # Применяем стили
                for col in range(1, 7):
                    cell = ws.cell(row=row, column=col)
                    cell.fill = fill
                    cell.border = thin_border
                    cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)

                ws.row_dimensions[row].height = 30
                row += 1

        # Заморозить первую строку
        ws.freeze_panes = "A2"

        # Добавить фильтры
        ws.auto_filter.ref = f"A1:F{row - 1}"

    def _add_stats_sheet(self, wb, slots_by_group: Dict, group_by_id: Dict):
        """Добавить лист со статистикой"""
        ws = wb.create_sheet("Статистика", 0)

        ws.cell(row=1, column=1, value="Статистика расписания")
        ws.cell(row=1, column=1).font = Font(bold=True, size=14)

        row = 3
        ws.cell(row=row, column=1, value="Группа")
        ws.cell(row=row, column=2, value="Занятий")
        ws.cell(row=row, column=3, value="Дней")
        ws.cell(row=row, column=4, value="Преподавателей")

        row += 1
        for group_id in sorted(slots_by_group.keys()):
            slots = slots_by_group[group_id]
            group = group_by_id.get(group_id)

            days = set(s.start_time.date() for s in slots)
            teachers = set(s.instructor for s in slots if s.instructor)

            ws.cell(row=row, column=1, value=group.name if group else f"Group {group_id}")
            ws.cell(row=row, column=2, value=len(slots))
            ws.cell(row=row, column=3, value=len(days))
            ws.cell(row=row, column=4, value=len(teachers))
            row += 1

    def export_to_pdf(
        self,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        single_date: Optional[str] = None,
        group_id: Optional[int] = None,
        instructor: Optional[str] = None,
        auditorium_ids: Optional[List[int]] = None,
        title_search: Optional[str] = None
    ) -> BytesIO:
        """
        Экспорт расписания в PDF формат (оптимизирован для печати).
        
        Args:
            date_from: Дата начала
            date_to: Дата конца
            single_date: Конкретная дата
            group_id: ID одной группы (для одного PDF)
            instructor: Фильтр по преподавателю
            auditorium_ids: Список ID аудиторий
            title_search: Фильтр по названию предмета
        """
        logger.info("=" * 60)
        logger.info("🚀 НАЧАЛО ЭКСПОРТА В PDF")
        logger.info("=" * 60)

        slots_by_group = self.get_slots_by_group(
            date_from=date_from,
            date_to=date_to,
            single_date=single_date,
            group_ids=[group_id] if group_id else None,
            instructor=instructor,
            auditorium_ids=auditorium_ids,
            title_search=title_search
        )

        if not slots_by_group:
            logger.warning("⚠️  По указанным фильтрам не найдено занятий")
            return BytesIO()

        output = BytesIO()
        
        if group_id and group_id in slots_by_group:
            logger.info(f"📄 Режим экспорта: одна группа (ID: {group_id})")
            # Один PDF для одной группы
            self._create_single_group_pdf(output, group_id, slots_by_group[group_id])
        else:
            logger.info("📄 Режим экспорта: несколько курсов")
            # Отдельные PDF для каждого курса
            self._create_multi_course_pdf(output, slots_by_group)

        output.seek(0)
        logger.info("✅ ЭКСПОРТ В PDF ЗАВЕРШЁН УСПЕШНО")
        logger.info("=" * 60)
        return output

    def _create_single_group_pdf(self, output: BytesIO, group_id: int, slots: List[ClassSlot]):
        """Создать PDF для одной группы"""
        group = self.db.query(Group).filter(Group.id == group_id).first()
        group_name = group.name if group else f"Group {group_id}"

        doc = SimpleDocTemplate(output, pagesize=landscape(A4), topMargin=0.5*cm, bottomMargin=0.5*cm)
        elements = []
        styles = getSampleStyleSheet()

        # Заголовок
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#366092'),
            spaceAfter=12,
            alignment=1  # CENTER
        )
        elements.append(Paragraph(f"Расписание группы {group_name}", title_style))

        # Таблица
        data = [["Дата", "День", "Время", "Предмет", "Преподаватель", "Аудитория"]]
        slots = sorted(slots, key=lambda s: s.start_time)

        for slot in slots:
            auditorium = self.db.query(Auditorium).filter(Auditorium.id == slot.auditorium_id).first()
            aud_name = auditorium.name if auditorium else "-"

            data.append([
                slot.start_time.strftime('%d.%m.%Y'),
                DAY_NAMES[slot.start_time.weekday()],
                slot.start_time.strftime('%H:%M'),
                slot.title,
                slot.instructor or "-",
                aud_name
            ])

        table = Table(data, colWidths=[2.5*cm, 1.5*cm, 1.5*cm, 5*cm, 3.5*cm, 2.5*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#366092')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F0F0F0')]),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        elements.append(table)
        doc.build(elements)

    def _create_multi_course_pdf(self, output: BytesIO, slots_by_group: Dict):
        """Создать PDF с разделением по курсам"""
        doc = SimpleDocTemplate(output, pagesize=landscape(A4), topMargin=0.5*cm, bottomMargin=0.5*cm)
        elements = []
        styles = getSampleStyleSheet()

        groups = self.db.query(Group).all()
        group_by_id = {g.id: g for g in groups}

        courses = self._extract_courses(slots_by_group, group_by_id)

        for course_idx, (course, group_ids) in enumerate(courses.items()):
            if course_idx > 0:
                elements.append(PageBreak())

            # Заголовок курса
            title_style = ParagraphStyle(
                'CourseTitle',
                parent=styles['Heading1'],
                fontSize=14,
                textColor=colors.HexColor(COURSE_COLORS.get(course, 'FFFFFF')),
                spaceAfter=12,
                alignment=1
            )
            elements.append(Paragraph(f"Расписание {course} курса", title_style))

            # Таблица для курса
            data = [["Группа", "Дата", "День", "Время", "Предмет", "Преподаватель", "Аудитория"]]

            for group_id in sorted(group_ids):
                if group_id not in slots_by_group:
                    continue

                group = group_by_id.get(group_id)
                group_name = group.name if group else f"Group {group_id}"

                slots = sorted(slots_by_group[group_id], key=lambda s: s.start_time)

                for slot in slots:
                    auditorium = self.db.query(Auditorium).filter(Auditorium.id == slot.auditorium_id).first()
                    aud_name = auditorium.name if auditorium else "-"

                    data.append([
                        group_name,
                        slot.start_time.strftime('%d.%m.%Y'),
                        DAY_NAMES[slot.start_time.weekday()],
                        slot.start_time.strftime('%H:%M'),
                        slot.title,
                        slot.instructor or "-",
                        aud_name
                    ])

            table = Table(data, colWidths=[2*cm, 2.2*cm, 1.3*cm, 1.3*cm, 4.5*cm, 3*cm, 2*cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#366092')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F0F0F0')]),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))

            elements.append(table)

        doc.build(elements)
