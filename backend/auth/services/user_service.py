from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException, status
from datetime import datetime, timezone
from typing import Optional, List

from database.models import User, UserRole, RefreshToken, LoginHistory, LoginStatus, Permission, UserPermission, AuditLog, AuditAction
from database.schemas import UserCreate, UserUpdate, UserResponse
from services.security import hash_password, verify_password, check_user_locked, increment_failed_login_attempts, reset_failed_login_attempts
from core.utils import mask_email, mask_ip


def get_user_by_id(user_id: int, db: Session) -> Optional[User]:
    """Получение пользователя по ID"""
    return db.query(User).filter(User.id == user_id).first()


def get_detailed_user(user_id: int, db: Session) -> Optional[User]:
    """Получение детальной информации о пользователе (SQLAlchemy объект)"""
    user = get_user_by_id(user_id, db)
    if not user:
        return None
    
    # Ищем последнюю успешную сессию
    last_login = db.query(LoginHistory).filter(
        LoginHistory.user_id == user_id,
        LoginHistory.status == LoginStatus.SUCCESS
    ).order_by(LoginHistory.created_at.desc()).first()
    
    # Ищем последнее изменение пароля в аудите
    last_password_change = db.query(AuditLog).filter(
        AuditLog.user_id == user_id,
        AuditLog.action == AuditAction.PASSWORD_CHANGE
    ).order_by(AuditLog.created_at.desc()).first()
    
    # Прикрепляем дополнительные поля прямо к объекту SQLAlchemy
    user.last_ip = last_login.ip_address if last_login else None
    user.last_user_agent = last_login.user_agent if last_login else None
    user.password_updated_at = last_password_change.created_at if last_password_change else None
    
    if last_login and last_login.user_agent:
        ua = last_login.user_agent.lower()
        if any(keyword in ua for keyword in ["mobile", "android", "iphone", "ipad"]):
            user.device_type = "mobile"
        elif "tablet" in ua:
            user.device_type = "tablet"
        else:
            user.device_type = "desktop"
    else:
        user.device_type = None
            
    return user


def get_user_by_email(email: str, db: Session) -> Optional[User]:
    """Получение пользователя по email"""
    return db.query(User).filter(User.email == email).first()


def create_user(user_data: UserCreate, db: Session) -> User:
    """Создание нового пользователя"""
    if get_user_by_email(user_data.email, db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )

    password_hash = hash_password(user_data.password)

    new_user = User(
        email=user_data.email,
        password_hash=password_hash,
        full_name=user_data.full_name,
        role=user_data.role or UserRole.STUDENT,
        is_active=True,
        is_verified=False
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


def update_user(user_id: int, user_data: UserUpdate, db: Session) -> User:
    """Обновление данных пользователя"""
    user = get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )

    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)

    return user


def authenticate_user(email: str, password: str, db: Session, ip_address: str = None, user_agent: str = None) -> User:
    """Аутентификация пользователя"""
    user = get_user_by_email(email, db)

    login_history = LoginHistory(
        email=mask_email(email),
        user_id=user.id if user else None,
        status=LoginStatus.FAILED,
        ip_address=mask_ip(ip_address) if ip_address else None,
        user_agent=user_agent
    )

    if not user:
        db.add(login_history)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные учетные данные"
        )

    if not user.is_active:
        db.add(login_history)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Аккаунт деактивирован"
        )

    if check_user_locked(user):
        login_history.status = LoginStatus.BLOCKED
        db.add(login_history)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"Аккаунт заблокирован до {user.locked_until}"
        )

    if not verify_password(password, user.password_hash):
        increment_failed_login_attempts(user, db)
        db.add(login_history)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные учетные данные"
        )

    reset_failed_login_attempts(user, db)
    login_history.status = LoginStatus.SUCCESS
    login_history.user_id = user.id
    login_history.ip_address = ip_address
    db.add(login_history)
    db.commit()

    return user


def get_user_permissions(user_id: int, db: Session) -> List[Permission]:
    """Получение всех разрешений пользователя"""
    user = get_user_by_id(user_id, db)
    if not user:
        return []

    permissions = []
    user_perms = db.query(UserPermission).filter(UserPermission.user_id == user_id).all()
    for up in user_perms:
        perm = db.query(Permission).filter(Permission.id == up.permission_id).first()
        if perm:
            permissions.append(perm)

    return permissions


def grant_permission(user_id: int, permission_id: int, db: Session) -> UserPermission:
    """Выдача разрешения пользователю"""
    user = get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    permission = db.query(Permission).filter(Permission.id == permission_id).first()
    if not permission:
        raise HTTPException(status_code=404, detail="Разрешение не найдено")

    existing = db.query(UserPermission).filter(
        and_(UserPermission.user_id == user_id, UserPermission.permission_id == permission_id)
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Разрешение уже выдано")

    user_permission = UserPermission(user_id=user_id, permission_id=permission_id)
    db.add(user_permission)
    db.commit()
    db.refresh(user_permission)

    return user_permission


def revoke_permission(user_id: int, permission_id: int, db: Session) -> None:
    """Отзыв разрешения"""
    user_permission = db.query(UserPermission).filter(
        and_(UserPermission.user_id == user_id, UserPermission.permission_id == permission_id)
    ).first()

    if not user_permission:
        raise HTTPException(status_code=404, detail="Разрешение не найдено")

    db.delete(user_permission)
    db.commit()


def get_login_history(user_id: int, limit: int = 50, db: Session = None) -> List[LoginHistory]:
    """История входов"""
    return db.query(LoginHistory).filter(
        LoginHistory.user_id == user_id
    ).order_by(LoginHistory.created_at.desc()).limit(limit).all()
