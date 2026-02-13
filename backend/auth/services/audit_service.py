"""Сервис для аудита действий пользователей"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from math import ceil
import json

from database.models import AuditLog, AuditAction, User
from database.schemas import AuditLogResponse, AuditLogFilter, AuditLogListResponse
from middleware.rate_limit import get_client_ip, get_user_agent
from core.utils import mask_ip
from fastapi import Request


def log_action(
    action: AuditAction,
    user_id: Optional[int],
    db: Session,
    details: Optional[Dict[str, Any]] = None,
    request: Optional[Request] = None
) -> AuditLog:
    """
    Логирование действия пользователя
    
    Args:
        action: Тип действия
        user_id: ID пользователя (None для системных действий)
        db: Сессия БД
        details: Дополнительные детали действия
        request: Request объект для получения IP и User-Agent
    
    Returns:
        Созданная запись аудита
    """
    ip_address = None
    user_agent = None
    
    if request:
        from middleware.rate_limit import get_client_ip, get_user_agent
        ip_address = get_client_ip(request)
        user_agent = get_user_agent(request)
    
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        details=json.dumps(details) if details else None,
        ip_address=mask_ip(ip_address) if ip_address else None,
        user_agent=user_agent
    )
    
    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)
    
    return audit_log


def get_audit_logs(params: AuditLogFilter, db: Session) -> AuditLogListResponse:
    """
    Получение записей аудита с фильтрацией и пагинацией
    
    Args:
        params: Параметры фильтрации
        db: Сессия БД
    
    Returns:
        Список записей аудита с метаданными пагинации
    """
    query = db.query(AuditLog)
    
    # Фильтр по пользователю
    if params.user_id:
        query = query.filter(AuditLog.user_id == params.user_id)
    
    # Фильтр по действию
    if params.action:
        try:
            action_enum = AuditAction(params.action)
            query = query.filter(AuditLog.action == action_enum)
        except ValueError:
            pass  # Игнорируем невалидные значения
    
    # Фильтр по дате
    if params.date_from:
        query = query.filter(AuditLog.created_at >= params.date_from)
    
    if params.date_to:
        query = query.filter(AuditLog.created_at <= params.date_to)
    
    # Подсчет общего количества
    total = query.count()
    
    # Сортировка по дате (новые сначала)
    query = query.order_by(desc(AuditLog.created_at))
    
    # Пагинация
    offset = (params.page - 1) * params.limit
    logs = query.offset(offset).limit(params.limit).all()
    
    # Вычисление количества страниц
    pages = ceil(total / params.limit) if total > 0 else 0
    
    return AuditLogListResponse(
        logs=[AuditLogResponse.model_validate(log) for log in logs],
        total=total,
        page=params.page,
        limit=params.limit,
        pages=pages
    )


def get_user_audit_logs(user_id: int, limit: int = 50, db: Session = None) -> List[AuditLogResponse]:
    """
    Получение истории действий конкретного пользователя
    
    Args:
        user_id: ID пользователя
        limit: Максимальное количество записей
        db: Сессия БД
    
    Returns:
        Список записей аудита
    """
    logs = db.query(AuditLog).filter(
        AuditLog.user_id == user_id
    ).order_by(desc(AuditLog.created_at)).limit(limit).all()
    
    return [AuditLogResponse.model_validate(log) for log in logs]

