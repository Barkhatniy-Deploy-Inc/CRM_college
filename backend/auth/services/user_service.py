from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException, status
from datetime import datetime, timezone
from typing import Optional, List

from database.models import User, UserRole, RefreshToken, LoginHistory, LoginStatus, Permission, UserPermission
from database.schemas import UserCreate, UserUpdate
from services.security import hash_password, verify_password, check_user_locked, increment_failed_login_attempts, reset_failed_login_attempts
from core.utils import mask_email, mask_ip


def get_user_by_id(user_id: int, db: Session) -> Optional[User]:
    """Получение пользователя по ID"""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(email: str, db: Session) -> Optional[User]:
    """Получение пользователя по email"""
    return db.query(User).filter(User.email == email).first()


def create_user(user_data: UserCreate, db: Session) -> User:
    """Создание нового пользователя"""
    # Проверка существования пользователя
    if get_user_by_email(user_data.email, db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )
    
    # Хеширование пароля
    password_hash = hash_password(user_data.password)
    
    # Создание пользователя
    new_user = User(
        email=user_data.email,
        password_hash=password_hash,
        full_name=user_data.full_name,
        role=user_data.role or UserRole.STUDENT,
        is_active=True,
        is_verified=False  # В будущем можно добавить email верификацию
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
    
    # Обновление полей
    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    return user


def authenticate_user(email: str, password: str, db: Session, ip_address: str = None, user_agent: str = None) -> User:
    """Аутентификация пользователя"""
    user = get_user_by_email(email, db)
    
    # Логируем попытку входа
    login_history = LoginHistory(
        email=mask_email(email),
        user_id=user.id if user else None,
        status=LoginStatus.FAILED,
        ip_address=mask_ip(ip_address) if ip_address else None,
        user_agent=user_agent
    )
    
    # Проверка существования пользователя
    if not user:
        db.add(login_history)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные учетные данные"
        )
    
    # Проверка активности
    if not user.is_active:
        db.add(login_history)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Аккаунт деактивирован"
        )
    
    # Проверка блокировки
    if check_user_locked(user):
        login_history.status = LoginStatus.BLOCKED
        db.add(login_history)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"Аккаунт заблокирован до {user.locked_until}"
        )
    
    # Проверка пароля
    if not verify_password(password, user.password_hash):
        increment_failed_login_attempts(user, db)
        db.add(login_history)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные учетные данные"
        )
    
    # Успешный вход
    reset_failed_login_attempts(user, db)
    login_history.status = LoginStatus.SUCCESS
    login_history.user_id = user.id
    db.add(login_history)
    db.commit()
    
    return user


def get_user_permissions(user_id: int, db: Session) -> List[Permission]:
    """Получение всех разрешений пользователя"""
    user = get_user_by_id(user_id, db)
    if not user:
        return []
    
    # Разрешения из роли (можно расширить логику)
    permissions = []
    
    # Прямые разрешения пользователя
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    permission = db.query(Permission).filter(Permission.id == permission_id).first()
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Разрешение не найдено"
        )
    
    # Проверка, не выдано ли уже разрешение
    existing = db.query(UserPermission).filter(
        and_(UserPermission.user_id == user_id, UserPermission.permission_id == permission_id)
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Разрешение уже выдано пользователю"
        )
    
    user_permission = UserPermission(user_id=user_id, permission_id=permission_id)
    db.add(user_permission)
    db.commit()
    db.refresh(user_permission)
    
    return user_permission


def revoke_permission(user_id: int, permission_id: int, db: Session) -> None:
    """Отзыв разрешения у пользователя"""
    user_permission = db.query(UserPermission).filter(
        and_(UserPermission.user_id == user_id, UserPermission.permission_id == permission_id)
    ).first()
    
    if not user_permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Разрешение не найдено"
        )
    
    db.delete(user_permission)
    db.commit()


def get_login_history(user_id: int, limit: int = 50, db: Session = None) -> List[LoginHistory]:
    """Получение истории входов пользователя"""
    return db.query(LoginHistory).filter(
        LoginHistory.user_id == user_id
    ).order_by(LoginHistory.created_at.desc()).limit(limit).all()

