from pydantic import BaseModel, EmailStr, ConfigDict, Field
from typing import Optional
from datetime import datetime
from enum import Enum

# ========== ENUMS ==========

class SlotStatus(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ParticipantStatus(str, Enum):
    REGISTERED = "registered"
    ATTENDED = "attended"
    ABSENT = "absent"

# ========== BASE MODELS ==========

class Base(BaseModel):
    model_config = ConfigDict(from_attributes=True)

# ========== AUTH MODELS ==========

class RegisterRequest(Base):
    email: EmailStr
    password: str
    full_name: str

class LoginRequest(Base):
    email: EmailStr
    password: str

class UserResponse(Base):
    id: int
    email: EmailStr
    full_name: str
    telegram_id: Optional[str] = None

class TokenResponse(Base):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# ========== AUDITORIUM MODELS ==========

class AuditoriumBase(Base):
    name: str
    capacity: Optional[int] = None
    description: Optional[str] = None

class AuditoriumCreate(AuditoriumBase):
    pass

class AuditoriumUpdate(Base):
    name: Optional[str] = None
    capacity: Optional[int] = None
    description: Optional[str] = None

class AuditoriumResponse(AuditoriumBase):
    id: int

# ========== COURSE MODELS ==========

class CourseBase(Base):
    name: str
    description: Optional[str] = None
    instructor: Optional[str] = None

class CourseCreate(CourseBase):
    pass

class CourseUpdate(Base):
    name: Optional[str] = None
    description: Optional[str] = None
    instructor: Optional[str] = None

class CourseResponse(CourseBase):
    id: int

# ========== SLOT MODELS ==========

class ClassSlotBase(Base):
    title: str
    start_time: datetime
    end_time: datetime
    instructor: Optional[str] = None
    max_participants: Optional[int] = None
    status: SlotStatus = SlotStatus.SCHEDULED

class ClassSlotCreate(ClassSlotBase):
    course_id: int
    auditorium_id: Optional[int] = None

class ClassSlotUpdate(Base):
    title: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    auditorium_id: Optional[int] = None
    instructor: Optional[str] = None
    max_participants: Optional[int] = None
    status: Optional[SlotStatus] = None

class ClassSlotResponse(ClassSlotBase):
    id: int
    course_id: int
    auditorium_id: Optional[int] = None

# ========== PARTICIPANT MODELS ==========

class AddParticipantRequest(Base):
    user_id: int

class ParticipantBase(Base):
    status: ParticipantStatus = ParticipantStatus.REGISTERED

class ParticipantCreate(ParticipantBase):
    class_slot_id: int
    user_id: int

class ParticipantUpdate(Base):
    status: Optional[ParticipantStatus] = None

class ParticipantResponse(ParticipantBase):
    id: int
    class_slot_id: int
    user_id: int
