import pytest
from fastapi import status

@pytest.mark.asyncio
async def test_get_subjects_empty(client, mock_auth):
    """Тест получения пустого списка предметов"""
    response = await client.get("/api/relations/subjects")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []

@pytest.mark.asyncio
async def test_create_subject(client, mock_auth):
    """Тест создания предмета"""
    payload = {"name": "История", "description": "Всеобщая история"}
    response = await client.post("/api/relations/subjects", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "История"
    assert "id" in data

@pytest.mark.asyncio
async def test_link_teacher_subject(client, mock_auth, db):
    """Теst связи преподавателя с предметом"""
    from database.models import Subject, User
    
    # Подготовка данных
    subject = Subject(name="Химия")
    teacher = User(full_name="Дмитрий Менделеев", email="mendeleev@example.com", password_hash="hash")
    db.add_all([subject, teacher])
    db.commit()
    
    payload = {"teacher_id": teacher.id, "subject_id": subject.id}
    response = await client.post("/api/relations/teacher-subject", json=payload)
    assert response.status_code == 201
    assert response.json()["teacher_id"] == teacher.id

@pytest.mark.asyncio
async def test_get_group_subjects(client, mock_auth, db):
    """Тест получения предметов группы (учебный план)"""
    from database.models import Subject, Group, GroupSubject
    
    group = Group(name="ИСП-31")
    sub1 = Subject(name="Математика")
    sub2 = Subject(name="Физика")
    db.add_all([group, sub1, sub2])
    db.commit()
    
    db.add(GroupSubject(group_id=group.id, subject_id=sub1.id))
    db.add(GroupSubject(group_id=group.id, subject_id=sub2.id))
    db.commit()
    
    response = await client.get(f"/api/relations/groups/{group.id}/subjects")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    names = [s["name"] for s in data]
    assert "Математика" in names
    assert "Физика" in names
