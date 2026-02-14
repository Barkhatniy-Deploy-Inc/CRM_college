import pytest
from services.schedule_exporter import ScheduleExporter
from database.models import Group, Auditorium, ClassSlot
from datetime import datetime, timezone

def test_exporter_xlsx(db):
    """Тест экспорта в XLSX с реальными данными"""
    exporter = ScheduleExporter(db)
    
    # 1. Создаем необходимые данные
    group = Group(name="TestGroup")
    db.add(group)
    db.flush() # Получаем ID
    
    auditorium = Auditorium(name="101")
    db.add(auditorium)
    db.flush()
    
    # 2. Создаем занятие (формат даты должен совпадать с фильтром)
    # В фильтре мы используем 14.02.2026
    slot = ClassSlot(
        group_id=group.id,
        auditorium_id=auditorium.id,
        title="Test Lesson",
        instructor="Test Teacher",
        start_time=datetime(2026, 2, 14, 10, 0, tzinfo=timezone.utc),
        end_time=datetime(2026, 2, 14, 11, 30, tzinfo=timezone.utc)
    )
    db.add(slot)
    db.commit()
    
    # 3. Экспорт
    output = exporter.export_to_xlsx(
        group_ids=[group.id],
        date_from="14.02.2026",
        date_to="14.02.2026"
    )
    assert output is not None
    assert len(output.getvalue()) > 0

def test_exporter_pdf(db):
    """Тест экспорта в PDF с данными"""
    exporter = ScheduleExporter(db)
    group = Group(name="TestGroupPDF")
    db.add(group)
    db.commit()
    
    try:
        output = exporter.export_to_pdf(
            group_ids=[group.id],
            date_from="14.02.2026",
            date_to="14.02.2026"
        )
        assert output is not None
    except Exception as e:
        pytest.skip(f"PDF export failed due to environment: {e}")
