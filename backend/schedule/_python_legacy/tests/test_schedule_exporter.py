"""
Автотесты для сервиса экспорта расписания (ScheduleExporter).
Тестирует фильтрацию, экспорт в XLSX и PDF форматы.
"""

import pytest
from datetime import datetime, timedelta
from io import BytesIO
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from database.models import Base, Group, Auditorium, ClassSlot
from services.schedule_exporter import ScheduleExporter
import logging

# Логирование
logger = logging.getLogger(__name__)


# === FIXTURES ===

@pytest.fixture(scope="function")
def test_db():
    """Создать тестовую БД в памяти"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def sample_groups(test_db: Session):
    """Создать тестовые группы"""
    groups = [
        Group(id=1, name="АБ-25/1-П", description="Группа 1 курса", instructor="Иванов"),
        Group(id=2, name="АБ-25/2-П", description="Группа 2 курса", instructor="Петров"),
        Group(id=3, name="АВ-25/3-П", description="Группа 3 курса", instructor="Сидоров"),
    ]
    for group in groups:
        test_db.add(group)
    test_db.commit()
    return groups


@pytest.fixture
def sample_auditoriums(test_db: Session):
    """Создать тестовые аудитории"""
    auditoriums = [
        Auditorium(id=1, name="Аудитория 101", capacity=30, description="Кабинет 1"),
        Auditorium(id=2, name="Аудитория 102", capacity=25, description="Кабинет 2"),
        Auditorium(id=3, name="Аудитория 103", capacity=40, description="Кабинет 3"),
    ]
    for aud in auditoriums:
        test_db.add(aud)
    test_db.commit()
    return auditoriums


@pytest.fixture
def sample_slots(test_db: Session, sample_groups, sample_auditoriums):
    """Создать тестовые занятия"""
    # Используем дату с сегодня на неделю
    today = datetime.now().replace(hour=0, minute=0, second=0)
    monday = today - timedelta(days=today.weekday())
    
    slots = [
        # Понедельник, группа 1, преподаватель Иванов
        ClassSlot(
            id=1,
            title="Математика",
            start_time=monday + timedelta(hours=9),
            end_time=monday + timedelta(hours=11),
            group_id=1,
            auditorium_id=1,
            instructor="Иванов"
        ),
        # Вторник, группа 1, преподаватель Иванов
        ClassSlot(
            id=2,
            title="Физика",
            start_time=monday + timedelta(days=1, hours=10),
            end_time=monday + timedelta(days=1, hours=12),
            group_id=1,
            auditorium_id=2,
            instructor="Иванов"
        ),
        # Понедельник, группа 2, преподаватель Петров
        ClassSlot(
            id=3,
            title="Математика",
            start_time=monday + timedelta(hours=11),
            end_time=monday + timedelta(hours=13),
            group_id=2,
            auditorium_id=2,
            instructor="Петров"
        ),
        # Среда, группа 2, преподаватель Петров
        ClassSlot(
            id=4,
            title="Химия",
            start_time=monday + timedelta(days=2, hours=9),
            end_time=monday + timedelta(days=2, hours=11),
            group_id=2,
            auditorium_id=3,
            instructor="Петров"
        ),
        # Четверг, группа 3, преподаватель Сидоров
        ClassSlot(
            id=5,
            title="Биология",
            start_time=monday + timedelta(days=3, hours=10),
            end_time=monday + timedelta(days=3, hours=12),
            group_id=3,
            auditorium_id=1,
            instructor="Сидоров"
        ),
        # Пятница, группа 3, преподаватель Петров
        ClassSlot(
            id=6,
            title="История",
            start_time=monday + timedelta(days=4, hours=9),
            end_time=monday + timedelta(days=4, hours=11),
            group_id=3,
            auditorium_id=2,
            instructor="Петров"
        ),
    ]
    for slot in slots:
        test_db.add(slot)
    test_db.commit()
    return slots


# === TESTS: ФИЛЬТРАЦИЯ ===

class TestFilterByInstructor:
    """Тесты фильтрации по преподавателю"""
    
    def test_filter_by_instructor_ivanov(self, test_db: Session, sample_slots):
        """Получить только занятия Иванова"""
        exporter = ScheduleExporter(test_db)
        slots_by_group = exporter.get_slots_by_group(instructor="Иванов")
        
        # Иванов ведёт занятия в группе 1 (2 слота) - всего 2
        assert len(slots_by_group) == 1
        assert 1 in slots_by_group
        assert len(slots_by_group[1]) == 2
    
    def test_filter_by_instructor_petrov(self, test_db: Session, sample_slots):
        """Получить только занятия Петрова"""
        exporter = ScheduleExporter(test_db)
        slots_by_group = exporter.get_slots_by_group(instructor="Петров")
        
        # Петров ведёт в группе 2 (2 слота) и группе 3 (1 слот)
        assert len(slots_by_group) == 2
        assert sum(len(v) for v in slots_by_group.values()) == 3
    
    def test_filter_by_instructor_partial_match(self, test_db: Session, sample_slots):
        """Тест частичного совпадения по преподавателю (case-insensitive)"""
        exporter = ScheduleExporter(test_db)
        
        # Частичное совпадение должно работать
        slots_by_group = exporter.get_slots_by_group(instructor="ван")
        assert len(slots_by_group) == 1
        
        # Case-insensitive
        slots_by_group = exporter.get_slots_by_group(instructor="ПЕТРОВ")
        assert len(slots_by_group) == 2


class TestFilterByAuditorium:
    """Тесты фильтрации по аудитории"""
    
    def test_filter_by_auditorium_single(self, test_db: Session, sample_slots):
        """Получить занятия в одной аудитории"""
        exporter = ScheduleExporter(test_db)
        slots_by_group = exporter.get_slots_by_group(auditorium_ids=[1])
        
        # Аудитория 1 имеет 2 слота
        assert sum(len(v) for v in slots_by_group.values()) == 2
    
    def test_filter_by_multiple_auditoriums(self, test_db: Session, sample_slots):
        """Получить занятия в нескольких аудиториях"""
        exporter = ScheduleExporter(test_db)
        slots_by_group = exporter.get_slots_by_group(auditorium_ids=[1, 2])
        
        # Аудитории 1 и 2 имеют в сумме 5 слотов
        assert sum(len(v) for v in slots_by_group.values()) == 5


class TestFilterByTitle:
    """Тесты фильтрации по названию предмета"""
    
    def test_filter_by_title_exact(self, test_db: Session, sample_slots):
        """Получить занятия по названию предмета (точное совпадение)"""
        exporter = ScheduleExporter(test_db)
        slots_by_group = exporter.get_slots_by_group(title_search="Математика")
        
        # Математика есть в группе 1 и 2
        assert len(slots_by_group) == 2
        assert sum(len(v) for v in slots_by_group.values()) == 2
    
    def test_filter_by_title_partial(self, test_db: Session, sample_slots):
        """Получить занятия по частичному совпадению названия"""
        exporter = ScheduleExporter(test_db)
        
        # Поиск по "матем" должен найти "Математика"
        slots_by_group = exporter.get_slots_by_group(title_search="матем")
        assert sum(len(v) for v in slots_by_group.values()) == 2
    
    def test_filter_by_title_case_insensitive(self, test_db: Session, sample_slots):
        """Тест case-insensitive поиска"""
        exporter = ScheduleExporter(test_db)
        
        slots_by_group = exporter.get_slots_by_group(title_search="ФИЗИКА")
        assert sum(len(v) for v in slots_by_group.values()) == 1


class TestCombinedFilters:
    """Тесты комбинированной фильтрации"""
    
    def test_filter_by_instructor_and_title(self, test_db: Session, sample_slots):
        """Фильтрация по преподавателю И названию предмета"""
        exporter = ScheduleExporter(test_db)
        slots_by_group = exporter.get_slots_by_group(
            instructor="Иванов",
            title_search="Физика"
        )
        
        # Иванов ведёт Физику в группе 1
        assert sum(len(v) for v in slots_by_group.values()) == 1
    
    def test_filter_by_instructor_and_auditorium(self, test_db: Session, sample_slots):
        """Фильтрация по преподавателю И аудитории"""
        exporter = ScheduleExporter(test_db)
        slots_by_group = exporter.get_slots_by_group(
            instructor="Петров",
            auditorium_ids=[2]
        )
        
        # Петров в аудитории 2 имеет несколько слотов
        assert sum(len(v) for v in slots_by_group.values()) >= 1
    
    def test_filter_by_group_and_instructor(self, test_db: Session, sample_slots):
        """Фильтрация по группе И преподавателю"""
        exporter = ScheduleExporter(test_db)
        slots_by_group = exporter.get_slots_by_group(
            group_ids=[2],
            instructor="Петров"
        )
        
        # Петров в группе 2 имеет 2 слота
        assert 2 in slots_by_group
        assert len(slots_by_group[2]) == 2
    
    def test_filter_by_all_criteria(self, test_db: Session, sample_slots):
        """Фильтрация по всем критериям одновременно"""
        exporter = ScheduleExporter(test_db)
        slots_by_group = exporter.get_slots_by_group(
            group_ids=[2],
            instructor="Петров",
            auditorium_ids=[3],
            title_search="Химия"
        )
        
        # Петров ведёт Химию в группе 2 в аудитории 3
        assert 2 in slots_by_group
        assert len(slots_by_group[2]) == 1


# === TESTS: ЭКСПОРТ ===

class TestXLSXExport:
    """Тесты экспорта в XLSX"""
    
    def test_export_xlsx_basic(self, test_db: Session, sample_slots):
        """Базовый экспорт в XLSX"""
        exporter = ScheduleExporter(test_db)
        result = exporter.export_to_xlsx()
        
        assert isinstance(result, BytesIO)
        assert result.getbuffer().nbytes > 0
    
    def test_export_xlsx_with_filter(self, test_db: Session, sample_slots):
        """Экспорт в XLSX с фильтром"""
        exporter = ScheduleExporter(test_db)
        result = exporter.export_to_xlsx(instructor="Иванов")
        
        assert isinstance(result, BytesIO)
        assert result.getbuffer().nbytes > 0
    
    def test_export_xlsx_with_separate_courses(self, test_db: Session, sample_slots):
        """Экспорт в XLSX с разделением по курсам"""
        exporter = ScheduleExporter(test_db)
        result = exporter.export_to_xlsx(separate_courses=True)
        
        assert isinstance(result, BytesIO)
        assert result.getbuffer().nbytes > 0
    
    def test_export_xlsx_with_stats(self, test_db: Session, sample_slots):
        """Экспорт в XLSX с добавлением статистики"""
        exporter = ScheduleExporter(test_db)
        result = exporter.export_to_xlsx(include_stats=True)
        
        assert isinstance(result, BytesIO)
        assert result.getbuffer().nbytes > 0
    
    def test_export_xlsx_empty_result(self, test_db: Session, sample_slots):
        """Экспорт в XLSX с пустым результатом"""
        exporter = ScheduleExporter(test_db)
        result = exporter.export_to_xlsx(instructor="Неизвестный преподаватель")
        
        assert isinstance(result, BytesIO)


class TestPDFExport:
    """Тесты экспорта в PDF"""
    
    def test_export_pdf_basic(self, test_db: Session, sample_slots):
        """Базовый экспорт в PDF"""
        exporter = ScheduleExporter(test_db)
        result = exporter.export_to_pdf()
        
        assert isinstance(result, BytesIO)
        assert result.getbuffer().nbytes > 0
    
    def test_export_pdf_single_group(self, test_db: Session, sample_slots):
        """Экспорт в PDF одной группы"""
        exporter = ScheduleExporter(test_db)
        result = exporter.export_to_pdf(group_id=1)
        
        assert isinstance(result, BytesIO)
        assert result.getbuffer().nbytes > 0
    
    def test_export_pdf_with_filter(self, test_db: Session, sample_slots):
        """Экспорт в PDF с фильтром"""
        exporter = ScheduleExporter(test_db)
        result = exporter.export_to_pdf(instructor="Петров")
        
        assert isinstance(result, BytesIO)
        assert result.getbuffer().nbytes > 0
    
    def test_export_pdf_empty_result(self, test_db: Session, sample_slots):
        """Экспорт в PDF с пустым результатом"""
        exporter = ScheduleExporter(test_db)
        result = exporter.export_to_pdf(instructor="Неизвестный преподаватель")
        
        assert isinstance(result, BytesIO)


# === TESTS: УТИЛИТЫ ===

class TestDateRangeHandling:
    """Тесты обработки диапазонов дат"""
    
    def test_date_range_single_date(self, test_db: Session):
        """Тест с конкретной датой"""
        exporter = ScheduleExporter(test_db)
        start, end = exporter.get_date_range(single_date="03.09.2025")
        
        assert start.date().strftime("%d.%m.%Y") == "03.09.2025"
        assert end.date().strftime("%d.%m.%Y") == "03.09.2025"
    
    def test_date_range_with_interval(self, test_db: Session):
        """Тест с диапазоном дат"""
        exporter = ScheduleExporter(test_db)
        start, end = exporter.get_date_range(
            date_from="01.09.2025",
            date_to="07.09.2025"
        )
        
        assert start.date().strftime("%d.%m.%Y") == "01.09.2025"
        assert end.date().strftime("%d.%m.%Y") == "07.09.2025"
    
    def test_date_range_default(self, test_db: Session):
        """Тест с дефолтным диапазоном (текущая неделя)"""
        exporter = ScheduleExporter(test_db)
        start, end = exporter.get_date_range()
        
        # Должны получить неделю
        delta = (end - start).days
        assert delta == 6


class TestCourseExtraction:
    """Тесты извлечения номера курса из названия группы"""
    
    def test_extract_course_number(self, test_db: Session):
        """Тест извлечения номера курса"""
        exporter = ScheduleExporter(test_db)
        
        assert exporter._extract_course_number("АБ-25/1-П") == 1
        assert exporter._extract_course_number("АБ-25/2-П") == 2
        assert exporter._extract_course_number("АВ-25/3-П") == 3
        assert exporter._extract_course_number("АЕ-25/4-П") == 4


# === ЗАПУСК ТЕСТОВ ===

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
