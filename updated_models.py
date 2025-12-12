"""
Обновленные модели для соответствия заявленной схеме БД
Эти модели заменят текущие модели в /workspace/backend/schedule/database/models.py
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Date, Time, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
from enum import Enum
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


# Таблицы для расписания в соответствии с заявленной схемой
class ScheduleTeacher(Base):
    __tablename__ = "schedule_teachers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)


class ScheduleAuditorium(Base):
    __tablename__ = "schedule_auditoriums"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)


class ScheduleGroup(Base):
    __tablename__ = "schedule_groups"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    course = Column(Integer, nullable=False)


class ScheduleSubject(Base):
    __tablename__ = "schedule_subjects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    teacher_id = Column(Integer, ForeignKey("schedule_teachers.id"), nullable=False)
    
    # Связь с преподавателем
    teacher = relationship("ScheduleTeacher")


class ScheduleLesson(Base):
    __tablename__ = "schedule_lessons"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    time_start = Column(Time, nullable=False)
    time_end = Column(Time, nullable=False)
    lesson_number = Column(Integer, nullable=False)
    group_id = Column(Integer, ForeignKey("schedule_groups.id"), nullable=False)
    subgroup = Column(String, nullable=True)
    subject_id = Column(Integer, ForeignKey("schedule_subjects.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("schedule_teachers.id"), nullable=False)
    auditorium_id = Column(Integer, ForeignKey("schedule_auditoriums.id"), nullable=False)
    activity_type = Column(String, nullable=True)
    comment = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Связи
    group = relationship("ScheduleGroup")
    subject = relationship("ScheduleSubject")
    teacher = relationship("ScheduleTeacher")
    auditorium = relationship("ScheduleAuditorium")


# Также нужно обновить остальные модели для согласованности
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    telegram_id = Column(String, nullable=True)
    
    # Добавляем поля, соответствующие схеме auth_db
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


# Pydantic схемы
class ScheduleTeacherBase(BaseModel):
    name: str

class ScheduleTeacherCreate(ScheduleTeacherBase):
    pass

class ScheduleTeacherUpdate(BaseModel):
    name: Optional[str] = None

class ScheduleTeacherResponse(ScheduleTeacherBase):
    id: int
    
    class Config:
        from_attributes = True


class ScheduleAuditoriumBase(BaseModel):
    name: str
    is_active: bool = True

class ScheduleAuditoriumCreate(ScheduleAuditoriumBase):
    pass

class ScheduleAuditoriumUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None

class ScheduleAuditoriumResponse(ScheduleAuditoriumBase):
    id: int
    
    class Config:
        from_attributes = True


class ScheduleGroupBase(BaseModel):
    name: str
    course: int

class ScheduleGroupCreate(ScheduleGroupBase):
    pass

class ScheduleGroupUpdate(BaseModel):
    name: Optional[str] = None
    course: Optional[int] = None

class ScheduleGroupResponse(ScheduleGroupBase):
    id: int
    
    class Config:
        from_attributes = True


class ScheduleSubjectBase(BaseModel):
    name: str
    teacher_id: int

class ScheduleSubjectCreate(ScheduleSubjectBase):
    pass

class ScheduleSubjectUpdate(BaseModel):
    name: Optional[str] = None
    teacher_id: Optional[int] = None

class ScheduleSubjectResponse(ScheduleSubjectBase):
    id: int
    
    class Config:
        from_attributes = True


class ScheduleLessonBase(BaseModel):
    date: datetime.date
    time_start: datetime.time
    time_end: datetime.time
    lesson_number: int
    group_id: int
    subject_id: int
    teacher_id: int
    auditorium_id: int
    subgroup: Optional[str] = None
    activity_type: Optional[str] = None
    comment: Optional[str] = None

class ScheduleLessonCreate(ScheduleLessonBase):
    pass

class ScheduleLessonUpdate(BaseModel):
    date: Optional[datetime.date] = None
    time_start: Optional[datetime.time] = None
    time_end: Optional[datetime.time] = None
    lesson_number: Optional[int] = None
    group_id: Optional[int] = None
    subject_id: Optional[int] = None
    teacher_id: Optional[int] = None
    auditorium_id: Optional[int] = None
    subgroup: Optional[str] = None
    activity_type: Optional[str] = None
    comment: Optional[str] = None

class ScheduleLessonResponse(ScheduleLessonBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True