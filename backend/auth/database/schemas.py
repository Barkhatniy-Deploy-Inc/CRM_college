from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from .models import UserRole, LoginStatus, AuditAction


# ============ User Schemas ============

class UserBase(BaseModel):
    email: EmailStr
    full_name: str


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Пароль должен содержать минимум 8 символов")
    role: Optional[UserRole] = UserRole.STUDENT


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None


class UserResponse(UserBase):
    id: int
    is_active: bool = True
    is_verified: bool = False
    role: UserRole
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    
    # Расширенные технические данные
    last_ip: Optional[str] = None
    last_user_agent: Optional[str] = None
    device_type: Optional[str] = None  # "desktop", "mobile", "tablet"

    model_config = ConfigDict(from_attributes=True)

class UserPublic(BaseModel):
    """Публичная информация о пользователе (без чувствительных данных)"""
    id: int
    email: EmailStr
    full_name: str
    role: UserRole
    
    model_config = ConfigDict(from_attributes=True)


# ============ Auth Schemas ============

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(UserCreate):
    pass


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Optional[UserResponse] = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class TokenData(BaseModel):
    """Данные внутри JWT токена"""
    user_id: int
    email: str
    role: UserRole
    exp: datetime


# ============ Password Schemas ============

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)


# ============ Permission Schemas ============

class PermissionBase(BaseModel):
    name: str
    description: Optional[str] = None
    resource: str
    action: str


class PermissionCreate(PermissionBase):
    pass


class PermissionResponse(PermissionBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)


class UserPermissionGrant(BaseModel):
    permission_id: int


class UserPermissionsResponse(BaseModel):
    user_id: int
    permissions: List[PermissionResponse]
    
    model_config = ConfigDict(from_attributes=True)


# ============ Login History Schemas ============

class LoginHistoryResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    email: str
    status: LoginStatus
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============ Session Schemas ============

class SessionResponse(BaseModel):
    """Информация о сессии"""
    id: int
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    device_name: Optional[str] = None
    created_at: datetime
    last_used_at: Optional[datetime] = None
    expires_at: datetime
    is_current: bool = False  # Текущая ли это сессия
    
    model_config = ConfigDict(from_attributes=True)


class SessionUpdate(BaseModel):
    """Обновление имени устройства"""
    device_name: Optional[str] = None


# ============ User Search Schemas ============

class UserSearchParams(BaseModel):
    """Параметры поиска пользователей"""
    search: Optional[str] = None  # Поиск по email/имени
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)
    sort: str = Field("created_at", pattern="^(created_at|email|full_name|last_login)$")
    order: str = Field("desc", pattern="^(asc|desc)$")


class UserListResponse(BaseModel):
    """Список пользователей с пагинацией"""
    users: List[UserResponse]
    total: int
    page: int
    limit: int
    pages: int


# ============ Audit Log Schemas ============

class AuditLogResponse(BaseModel):
    """Запись аудита"""
    id: int
    user_id: Optional[int] = None
    action: str
    details: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class AuditLogFilter(BaseModel):
    """Фильтры для аудита"""
    user_id: Optional[int] = None
    action: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    page: int = Field(1, ge=1)
    limit: int = Field(50, ge=1, le=100)


class AuditLogListResponse(BaseModel):
    """Список записей аудита"""
    logs: List[AuditLogResponse]
    total: int
    page: int
    limit: int
    pages: int


# ============ Health Check ============

class HealthResponse(BaseModel):
    status: str
    database: str
    version: str

