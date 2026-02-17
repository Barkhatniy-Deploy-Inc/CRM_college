from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SQLAlchemyEnum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
from enum import Enum
from datetime import datetime


class UserRole(str, Enum):
    """Роли пользователей"""
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"
    MODERATOR = "moderator"


class LoginStatus(str, Enum):
    """Статусы попыток входа"""
    SUCCESS = "success"
    FAILED = "failed"
    BLOCKED = "blocked"


class User(Base):
    """Модель пользователя"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    role = Column(SQLAlchemyEnum(UserRole), default=UserRole.STUDENT, nullable=False)
    
    # Защита от брутфорса
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime, nullable=True)
    
    # Метаданные
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Связи
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    login_history = relationship("LoginHistory", back_populates="user", cascade="all, delete-orphan")
    user_permissions = relationship("UserPermission", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")


class RefreshToken(Base):
    """Модель refresh токена (сессии)"""
    __tablename__ = "refresh_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String, unique=True, index=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_used_at = Column(DateTime(timezone=True), nullable=True)  # Последнее использование
    is_revoked = Column(Boolean, default=False, nullable=False)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    device_name = Column(String, nullable=True)  # Имя устройства (опционально)
    
    user = relationship("User", back_populates="refresh_tokens")


class LoginHistory(Base):
    """История входов пользователей"""
    __tablename__ = "login_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)  # nullable для неудачных попыток
    email = Column(String, nullable=False)  # Сохраняем email даже если пользователь не найден
    status = Column(SQLAlchemyEnum(LoginStatus), nullable=False)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    user = relationship("User", back_populates="login_history")


class Permission(Base):
    """Модель разрешений"""
    __tablename__ = "permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    resource = Column(String, nullable=False)  # Например: "schedule", "users", "auditoriums"
    action = Column(String, nullable=False)  # Например: "create", "read", "update", "delete"
    
    user_permissions = relationship("UserPermission", back_populates="permission")


class UserPermission(Base):
    """Связь пользователей и разрешений (многие ко многим)"""
    __tablename__ = "user_permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    permission_id = Column(Integer, ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False)
    granted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    user = relationship("User", back_populates="user_permissions")
    permission = relationship("Permission", back_populates="user_permissions")


class AuditAction(str, Enum):
    """Типы действий для аудита"""
    PASSWORD_CHANGE = "password_change"
    ROLE_CHANGE = "role_change"
    PROFILE_UPDATE = "profile_update"
    EMAIL_CHANGE = "email_change"
    USER_CREATED = "user_created"
    USER_DELETED = "user_deleted"
    USER_ACTIVATED = "user_activated"
    USER_DEACTIVATED = "user_deactivated"
    PERMISSION_GRANTED = "permission_granted"
    PERMISSION_REVOKED = "permission_revoked"
    SESSION_REVOKED = "session_revoked"
    LOGIN = "login"
    LOGOUT = "logout"
    
    # Расписание
    SCHEDULE_EDITED = "schedule_edited"
    SCHEDULE_IMPORTED = "schedule_imported"
    SCHEDULE_DELETED = "schedule_deleted"
    
    # Техкарты
    TECHCARD_CREATED = "techcard_created"
    TECHCARD_EXPORTED = "techcard_exported"
    
    # Безопасность
    SECURITY_ALERT = "security_alert"
    UNAUTHORIZED_ACCESS = "unauthorized_access"


class AuditLog(Base):
    """Модель аудита действий пользователей"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)  # nullable для системных действий
    action = Column(SQLAlchemyEnum(AuditAction), nullable=False)
    details = Column(Text, nullable=True)  # JSON детали действия
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    user = relationship("User", back_populates="audit_logs")

