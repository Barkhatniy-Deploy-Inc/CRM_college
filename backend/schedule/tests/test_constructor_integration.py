import pytest
from fastapi import status
from datetime import datetime, timedelta

@pytest.mark.asyncio
async def test_create_slot_with_subject(client, mock_auth, db):
    """Тест создания урока с привязкой к предмету и преподавателю"""
    from database.models import Subject, Group, User
    
    subject = Subject(name="Математика")
    group = Group(name="ИСП-21")
    teacher = User(full_name="Иванов И.И.", email="ivanov@example.com", password_hash="hash")
    db.add_all([subject, group, teacher])
    db.commit()
    
    payload = {
        "title": "Высшая математика",
        "subject_id": subject.id,
        "group_id": group.id,
        "instructor": teacher.full_name,
        "instructor_id": teacher.id,
        "start_time": datetime.now().isoformat(),
        "end_time": (datetime.now() + timedelta(hours=1.5)).isoformat()
    }
    
    response = await client.post("/api/schedule/", json=payload)
    assert response.status_code in [200, 201]
    data = response.json()
    assert data["subject_id"] == subject.id
    assert data["instructor_id"] == teacher.id

@pytest.mark.asyncio
async def test_update_slot_override(client, mock_auth, db):
    """Тест локальной замены преподавателя в уроке"""
    from database.models import ClassSlot, Group, User
    
    group = Group(name="ИСП-21")
    db.add(group)
    db.commit()
    
    slot = ClassSlot(
        title="Оригинальный урок",
        group_id=group.id,
        start_time=datetime.now(),
        end_time=datetime.now() + timedelta(hours=1.5),
        instructor="Оригинальный препод"
    )
    db.add(slot)
    db.commit()
    
    # Локальная замена
    payload = {"instructor": "Заменяющий препод"}
    response = await client.put(f"/api/schedule/{slot.id}", json=payload)
    assert response.status_code == 200
    assert response.json()["instructor"] == "Заменяющий препод"
