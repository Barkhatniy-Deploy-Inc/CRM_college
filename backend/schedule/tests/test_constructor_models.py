import pytest
from sqlalchemy.orm import Session
from database.models import Subject, TeacherSubject, SubjectAuditorium, User, Auditorium, Group

def test_create_subject(db: Session):
    """Тест создания предмета"""
    subject = Subject(name="Математика", description="Высшая математика")
    db.add(subject)
    db.commit()
    
    assert subject.id is not None
    assert subject.name == "Математика"

def test_teacher_subject_relation(db: Session):
    """Тест связи Преподаватель - Предмет"""
    teacher = User(full_name="Иван Иванов", email="teacher@example.com", password_hash="hash")
    subject = Subject(name="Программирование")
    db.add_all([teacher, subject])
    db.commit()
    
    relation = TeacherSubject(teacher_id=teacher.id, subject_id=subject.id)
    db.add(relation)
    db.commit()
    
    assert relation.id is not None
    assert relation.teacher_id == teacher.id
    assert relation.subject_id == subject.id

def test_subject_auditorium_relation(db: Session):
    """Тест связи Предмет - Кабинет"""
    subject = Subject(name="Физика")
    auditorium = Auditorium(name="Каб. 101", capacity=30)
    db.add_all([subject, auditorium])
    db.commit()
    
    relation = SubjectAuditorium(subject_id=subject.id, auditorium_id=auditorium.id)
    db.add(relation)
    db.commit()
    
    assert relation.id is not None
    assert relation.subject_id == subject.id
    assert relation.auditorium_id == auditorium.id

def test_group_subject_relation(db: Session):
    """Тест связи Группа - Предмет (учебный план)"""
    from database.models import GroupSubject
    group = Group(name="ИСП-21")
    subject = Subject(name="Базы данных")
    db.add_all([group, subject])
    db.commit()
    
    relation = GroupSubject(group_id=group.id, subject_id=subject.id)
    db.add(relation)
    db.commit()
    
    assert relation.id is not None
    assert relation.group_id == group.id
    assert relation.subject_id == subject.id

def test_class_slot_subject_relation(db: Session):
    """Тест связи Урока с Предметом"""
    from database.models import ClassSlot, SlotStatus
    from datetime import datetime, timedelta
    
    subject = Subject(name="Математика")
    group = Group(name="ИСП-21")
    db.add_all([subject, group])
    db.commit()
    
    slot = ClassSlot(
        title="Пара 1",
        subject_id=subject.id,
        group_id=group.id,
        start_time=datetime.now(),
        end_time=datetime.now() + timedelta(hours=1.5),
        instructor="Иванов И.И."
    )
    db.add(slot)
    db.commit()
    
    assert slot.id is not None
    assert slot.subject_id == subject.id
    assert slot.subject.name == "Математика"
