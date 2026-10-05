from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database.database import get_db
from database.models import (
    Subject, SubjectCreate, SubjectResponse,
    TeacherSubject, TeacherSubjectLink, TeacherSubjectResponse,
    GroupSubject, GroupSubjectLink, GroupSubjectResponse,
    SubjectAuditorium, SubjectAuditoriumLink, SubjectAuditoriumResponse
)
from dependencies import require_roles

router = APIRouter(prefix="/api/relations", tags=["🔗 Связи (Конструктор)"])

_editor = require_roles("admin", "moderator")

# --- Subjects ---

@router.get("/subjects", response_model=List[SubjectResponse])
def get_subjects(db: Session = Depends(get_db)):
    return db.query(Subject).all()

@router.post("/subjects", response_model=SubjectResponse, status_code=201)
def create_subject(subject: SubjectCreate, u: dict = Depends(_editor), db: Session = Depends(get_db)):
    db_subject = Subject(**subject.model_dump())
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    return db_subject

# --- Teacher - Subject ---

@router.post("/teacher-subject", response_model=TeacherSubjectResponse, status_code=201)
def link_teacher_subject(link: TeacherSubjectLink, u: dict = Depends(_editor), db: Session = Depends(get_db)):
    db_link = TeacherSubject(**link.model_dump())
    db.add(db_link)
    db.commit()
    db.refresh(db_link)
    return db_link

# --- Group - Subject (Учебный план) ---

@router.get("/groups/{group_id}/subjects", response_model=List[SubjectResponse])
def get_group_subjects(group_id: int, db: Session = Depends(get_db)):
    subjects = db.query(Subject).join(GroupSubject).filter(GroupSubject.group_id == group_id).all()
    return subjects

@router.post("/group-subject", response_model=GroupSubjectResponse, status_code=201)
def link_group_subject(link: GroupSubjectLink, u: dict = Depends(_editor), db: Session = Depends(get_db)):
    db_link = GroupSubject(**link.model_dump())
    db.add(db_link)
    db.commit()
    db.refresh(db_link)
    return db_link

# --- Subject - Auditorium ---

@router.post("/subject-auditorium", response_model=SubjectAuditoriumResponse, status_code=201)
def link_subject_auditorium(link: SubjectAuditoriumLink, u: dict = Depends(_editor), db: Session = Depends(get_db)):
    db_link = SubjectAuditorium(**link.model_dump())
    db.add(db_link)
    db.commit()
    db.refresh(db_link)
    return db_link
