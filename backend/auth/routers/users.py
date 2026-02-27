from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional

from database.database import get_db
from database.models import User, UserRole
from database.schemas import (
    UserResponse, UserUpdate, UserPublic, UserSearchParams, UserListResponse,
    LoginHistoryResponse, AuditLogResponse, AuditLogFilter, AuditLogListResponse
)
from services.user_service import get_user_by_id, update_user, get_login_history, get_detailed_user
from services.security import hash_password
from services.search_service import search_users
from services.audit_service import get_audit_logs, get_user_audit_logs, log_action, AuditAction
from dependencies import get_current_active_user, require_role

router = APIRouter(prefix="/api/users", tags=["👥 Пользователи"])


# Удален дублирующий эндпоинт /me - используйте /api/auth/me


@router.get("/me/history", response_model=List[LoginHistoryResponse])
async def get_my_login_history(
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Получение истории входов текущего пользователя"""
    history = get_login_history(current_user.id, limit, db)
    return [LoginHistoryResponse.model_validate(h) for h in history]


@router.get("/{user_id}", response_model=UserPublic)
async def get_user(
    user_id: int,
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.MODERATOR)),
    db: Session = Depends(get_db)
):
    """Получение информации о пользователе (только для админов и модераторов)"""
    user = get_detailed_user(user_id, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    return UserPublic.model_validate(user)


@router.put("/me", response_model=UserResponse)
async def update_me(
    data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    request: Request = None,
    db: Session = Depends(get_db)
):
    """Обновление данных текущего пользователя"""
    # Нельзя изменить роль через этот endpoint
    if data.role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нельзя изменить роль самостоятельно"
        )
    
    updated_user = update_user(current_user.id, data, db)
    
    # Логирование в аудит
    log_action(
        AuditAction.PROFILE_UPDATE,
        current_user.id,
        db,
        {"fields_updated": list(data.model_dump(exclude_unset=True).keys())},
        request
    )
    
    return UserResponse.model_validate(updated_user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user_admin(
    user_id: int,
    data: UserUpdate,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    request: Request = None,
    db: Session = Depends(get_db)
):
    """Обновление данных пользователя (только для админов)"""
    old_user = get_user_by_id(user_id, db)
    if not old_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    # Логирование изменений
    changes = {}
    if data.role and data.role != old_user.role:
        changes["role"] = {"old": old_user.role.value, "new": data.role.value}
        log_action(AuditAction.ROLE_CHANGE, user_id, db, changes, request)
    
    updated_user = update_user(user_id, data, db)
    
    # Логирование обновления профиля
    if not changes.get("role"):
        log_action(AuditAction.PROFILE_UPDATE, user_id, db, {"updated_by": current_user.id}, request)
    
    return UserResponse.model_validate(updated_user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_details(
    user_id: int,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """
    Получение детальной информации о пользователе (только для админов)
    """
    user = get_detailed_user(user_id, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    return UserResponse.model_validate(user)


# ============ Поиск пользователей ============

@router.get("", response_model=UserListResponse)
async def search_users_endpoint(
    search: Optional[str] = Query(None, description="Поиск по email или имени"),
    role: Optional[UserRole] = Query(None, description="Фильтр по роли"),
    is_active: Optional[bool] = Query(None, description="Фильтр по активности"),
    is_verified: Optional[bool] = Query(None, description="Фильтр по верификации"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    limit: int = Query(20, ge=1, le=100, description="Количество на странице"),
    sort: str = Query("created_at", pattern="^(created_at|email|full_name|last_login)$", description="Поле сортировки"),
    order: str = Query("desc", pattern="^(asc|desc)$", description="Направление сортировки"),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.MODERATOR)),
    db: Session = Depends(get_db)
):
    """
    Поиск и фильтрация пользователей (только для админов и модераторов)
    """
    params = UserSearchParams(
        search=search,
        role=role,
        is_active=is_active,
        is_verified=is_verified,
        page=page,
        limit=limit,
        sort=sort,
        order=order
    )
    
    return search_users(params, db)


# ============ Аудит действий ============

@router.put("/{user_id}/password", response_model=UserResponse)
async def reset_user_password(
    user_id: int,
    new_password: str = Query(..., min_length=8),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    request: Request = None,
    db: Session = Depends(get_db)
):
    """Принудительная смена пароля пользователя администратором"""
    user = get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    user.password_hash = hash_password(new_password)
    db.commit()
    
    log_action(
        AuditAction.PASSWORD_CHANGE, 
        user_id, 
        db, 
        {"changed_by": current_user.id, "type": "admin_reset"}, 
        request
    )
    
    return UserResponse.model_validate(user)
    """
    Получение истории действий пользователя (только для админов и модераторов)
    """
    # Проверка существования пользователя
    user = get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    return get_user_audit_logs(user_id, limit, db)


@router.get("/audit-log/all", response_model=AuditLogListResponse)
async def get_all_audit_logs(
    user_id: Optional[int] = Query(None, description="Фильтр по пользователю"),
    action: Optional[str] = Query(None, description="Фильтр по действию"),
    date_from: Optional[str] = Query(None, description="Дата от (ISO format)"),
    date_to: Optional[str] = Query(None, description="Дата до (ISO format)"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """
    Получение всех записей аудита с фильтрацией (только для админов)
    """
    from datetime import datetime
    
    params = AuditLogFilter(
        user_id=user_id,
        action=action,
        date_from=datetime.fromisoformat(date_from) if date_from else None,
        date_to=datetime.fromisoformat(date_to) if date_to else None,
        page=page,
        limit=limit
    )
    
    return get_audit_logs(params, db)


@router.post("/audit-log/internal", status_code=status.HTTP_201_CREATED)
async def create_internal_audit_log(
    data: dict,
    db: Session = Depends(get_db)
):
    """
    Внутренний эндпоинт для создания логов из других сервисов.
    """
    from services.audit_service import log_action
    from database.models import AuditAction
    
    try:
        action_val = data.get("action")
        try:
            action = AuditAction(action_val)
        except ValueError:
            action = AuditAction.SECURITY_ALERT
            
        log_action(
            action=action,
            user_id=data.get("user_id"),
            db=db,
            details=data.get("details", {})
        )
        return {"status": "logged"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

