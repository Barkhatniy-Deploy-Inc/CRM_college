from sqlalchemy import Column, Integer, String, DateTime, Date, Time, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
from enum import Enum
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


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
    course = Column(Integer)


class ScheduleSubject(Base):
    __tablename__ = "schedule_subjects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    teacher_id = Column(Integer, ForeignKey("schedule_teachers.id"))


class ScheduleLesson(Base):
    __tablename__ = "schedule_lessons"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    time_start = Column(Time, nullable=False)
    time_end = Column(Time, nullable=False)
    lesson_number = Column(Integer)
    group_id = Column(Integer, ForeignKey("schedule_groups.id"))
    subgroup = Column(Integer)
    subject_id = Column(Integer, ForeignKey("schedule_subjects.id"))
    teacher_id = Column(Integer, ForeignKey("schedule_teachers.id"))
    auditorium_id = Column(Integer, ForeignKey("schedule_auditoriums.id"))
    activity_type = Column(String)
    comment = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Связи
    group = relationship("ScheduleGroup")
    teacher = relationship("ScheduleTeacher")
    subject = relationship("ScheduleSubject")
    auditorium = relationship("ScheduleAuditorium")


# Pydantic модели для API
class ScheduleTeacherBase(BaseModel):
    name: str

class ScheduleTeacherCreate(ScheduleTeacherBase):
    pass

class ScheduleTeacherResponse(ScheduleTeacherBase):
    id: int
    
    class Config:
        from_attributes = True


class ScheduleAuditoriumBase(BaseModel):
    name: str
    is_active: bool = True

class ScheduleAuditoriumCreate(ScheduleAuditoriumBase):
    pass

class ScheduleAuditoriumResponse(ScheduleAuditoriumBase):
    id: int
    
    class Config:
        from_attributes = True


class ScheduleGroupBase(BaseModel):
    name: str
    course: Optional[int] = None

class ScheduleGroupCreate(ScheduleGroupBase):
    pass

class ScheduleGroupResponse(ScheduleGroupBase):
    id: int
    
    class Config:
        from_attributes = True


class ScheduleSubjectBase(BaseModel):
    name: str
    teacher_id: int

class ScheduleSubjectCreate(ScheduleSubjectBase):
    pass

class ScheduleSubjectResponse(ScheduleSubjectBase):
    id: int
    
    class Config:
        from_attributes = True


class ScheduleLessonBase(BaseModel):
    date: datetime
    time_start: datetime
    time_end: datetime
    lesson_number: Optional[int] = None
    group_id: int
    subgroup: Optional[int] = None
    subject_id: int
    teacher_id: int
    auditorium_id: int
    activity_type: Optional[str] = None
    comment: Optional[str] = None

class ScheduleLessonCreate(ScheduleLessonBase):
    pass

class ScheduleLessonResponse(ScheduleLessonBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
