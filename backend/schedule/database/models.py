from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from .database import Base
from enum import Enum
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class SlotStatus(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ParticipantStatus(str, Enum):
    REGISTERED = "registered"
    ATTENDED = "attended"
    ABSENT = "absent"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    telegram_id = Column(String, nullable=True)
    participants = relationship("Participant", back_populates="user")
    subjects = relationship("TeacherSubject", back_populates="teacher")

class Subject(Base):
    __tablename__ = "subjects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    
    teachers = relationship("TeacherSubject", back_populates="subject")
    auditoriums = relationship("SubjectAuditorium", back_populates="subject")
    groups = relationship("GroupSubject", back_populates="subject")
    slots = relationship("ClassSlot", back_populates="subject")

class TeacherSubject(Base):
    __tablename__ = "teacher_subjects"
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("users.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    
    teacher = relationship("User", back_populates="subjects")
    subject = relationship("Subject", back_populates="teachers")

class GroupSubject(Base):
    __tablename__ = "group_subjects"
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    
    group = relationship("Group", back_populates="subjects")
    subject = relationship("Subject", back_populates="groups")

class SubjectAuditorium(Base):
    __tablename__ = "subject_auditoriums"
    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    auditorium_id = Column(Integer, ForeignKey("auditoriums.id"))
    
    subject = relationship("Subject", back_populates="auditoriums")
    auditorium = relationship("Auditorium", back_populates="subject_links")

class Auditorium(Base):
    __tablename__ = "auditoriums"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    capacity = Column(Integer)
    description = Column(String)
    slots = relationship("ClassSlot", back_populates="auditorium")
    subject_links = relationship("SubjectAuditorium", back_populates="auditorium")

class Group(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    instructor = Column(String) # Куратор
    slots = relationship("ClassSlot", back_populates="group")
    subjects = relationship("GroupSubject", back_populates="group")

class ClassSlot(Base):
    __tablename__ = "class_slots"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    instructor = Column(String) # Отображаемое имя преподавателя
    instructor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    max_participants = Column(Integer)
    status = Column(SQLAlchemyEnum(SlotStatus), default=SlotStatus.SCHEDULED)
    group_id = Column(Integer, ForeignKey("groups.id"))
    auditorium_id = Column(Integer, ForeignKey("auditoriums.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=True)
    
    group = relationship("Group", back_populates="slots")
    auditorium = relationship("Auditorium", back_populates="slots")
    subject = relationship("Subject", back_populates="slots")
    participants = relationship("Participant", back_populates="slot")
    teacher = relationship("User")

class Participant(Base):
    __tablename__ = "participants"
    id = Column(Integer, primary_key=True, index=True)
    class_slot_id = Column(Integer, ForeignKey("class_slots.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    status = Column(SQLAlchemyEnum(ParticipantStatus), default=ParticipantStatus.REGISTERED)
    slot = relationship("ClassSlot", back_populates="participants")
    user = relationship("User", back_populates="participants")

# Pydantic models for request and response
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    telegram_id: Optional[str] = None
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class AuditoriumBase(BaseModel):
    name: str
    capacity: Optional[int] = None
    description: Optional[str] = None

class AuditoriumCreate(AuditoriumBase):
    pass

class AuditoriumUpdate(BaseModel):
    name: Optional[str] = None
    capacity: Optional[int] = None
    description: Optional[str] = None

class AuditoriumResponse(AuditoriumBase):
    id: int
    class Config:
        from_attributes = True

class GroupBase(BaseModel):
    name: str
    description: Optional[str] = None
    instructor: Optional[str] = None

class GroupCreate(GroupBase):
    pass

class GroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    instructor: Optional[str] = None

class GroupResponse(GroupBase):
    id: int
    class Config:
        from_attributes = True

class ClassSlotBase(BaseModel):
    title: str
    start_time: datetime
    end_time: datetime
    instructor: Optional[str] = None
    max_participants: Optional[int] = None
    status: SlotStatus = SlotStatus.SCHEDULED

class ClassSlotCreate(ClassSlotBase):
    group_id: int
    auditorium_id: Optional[int] = None

class ClassSlotUpdate(BaseModel):
    title: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    auditorium_id: Optional[int] = None
    instructor: Optional[str] = None
    max_participants: Optional[int] = None
    status: Optional[SlotStatus] = None

class ClassSlotResponse(ClassSlotBase):
    id: int
    group_id: int
    auditorium_id: Optional[int] = None
    class Config:
        from_attributes = True

class AddParticipantRequest(BaseModel):
    user_id: int

class ParticipantBase(BaseModel):
    status: ParticipantStatus = ParticipantStatus.REGISTERED

class ParticipantCreate(ParticipantBase):
    class_slot_id: int
    user_id: int

class ParticipantUpdate(BaseModel):
    status: Optional[ParticipantStatus] = None

class ParticipantResponse(ParticipantBase):
    id: int
    class_slot_id: int
    user_id: int
    class Config:
        from_attributes = True

# ============ Relations Schemas ============

class SubjectBase(BaseModel):
    name: str
    description: Optional[str] = None

class SubjectCreate(SubjectBase):
    pass

class SubjectResponse(SubjectBase):
    id: int
    class Config:
        from_attributes = True

class TeacherSubjectLink(BaseModel):
    teacher_id: int
    subject_id: int

class TeacherSubjectResponse(TeacherSubjectLink):
    id: int
    class Config:
        from_attributes = True

class GroupSubjectLink(BaseModel):
    group_id: int
    subject_id: int

class GroupSubjectResponse(GroupSubjectLink):
    id: int
    class Config:
        from_attributes = True

class SubjectAuditoriumLink(BaseModel):
    subject_id: int
    auditorium_id: int

class SubjectAuditoriumResponse(SubjectAuditoriumLink):
    id: int
    class Config:
        from_attributes = True
