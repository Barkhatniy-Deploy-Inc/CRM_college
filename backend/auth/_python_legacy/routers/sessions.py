"""Роутер для управления сессиями"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Optional

from database.database import get_db
from database.models import User, RefreshToken
from database.schemas import SessionResponse, SessionUpdate
from dependencies import get_current_active_user
from services.session_service import (
    get_user_sessions, update_session_device_name,
    revoke_session, revoke_all_other_sessions
)
from services.token_service import revoke_refresh_token
from services.audit_service import log_action, AuditAction

router = APIRouter(prefix="/api/auth/sessions", tags=["🔐 Сессии"])


def get_current_token_id(request: Optional[Request], db: Session) -> Optional[int]:
    """Получение ID текущей сессии из токена"""
    refresh_token_cookie = request.cookies.get("refresh_token") if request else None
    if not refresh_token_cookie:
        return None
    
    try:
        payload = decode_token(refresh_token_cookie)
        if payload.get("type") != "refresh":
            return None
        
        # Находим сессию по токену
        session = db.query(RefreshToken).filter(
            RefreshToken.token == refresh_token_cookie
        ).first()
        
        return session.id if session else None
    except:
        return None


@router.get("", response_model=list[SessionResponse])
async def get_sessions(
    current_user: User = Depends(get_current_active_user),
    request: Request = None,
    db: Session = Depends(get_db)
):
    """
    Получение списка всех активных сессий текущего пользователя
    """
    current_token_id = get_current_token_id(request, db) if request else None
    sessions = get_user_sessions(current_user.id, current_token_id, db)
    return sessions


@router.put("/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: int,
    data: SessionUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    Обновление имени устройства для сессии
    """
    session = update_session_device_name(session_id, current_user.id, data.device_name or "", db)
    
    # Логирование в аудит
    log_action(
        AuditAction.SESSION_REVOKED,  # Используем существующий тип, можно добавить SESSION_UPDATED
        current_user.id,
        db,
        {"session_id": session_id, "device_name": data.device_name},
        request
    )
    
    return SessionResponse(
        id=session.id,
        ip_address=session.ip_address,
        user_agent=session.user_agent,
        device_name=session.device_name,
        created_at=session.created_at,
        last_used_at=session.last_used_at,
        expires_at=session.expires_at,
        is_current=False
    )


@router.delete("/{session_id}")
async def revoke_session_endpoint(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    Отзыв конкретной сессии
    """
    # Получаем токен сессии перед отзывом
    session = db.query(RefreshToken).filter(
        RefreshToken.id == session_id,
        RefreshToken.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сессия не найдена"
        )
    
    revoke_session(session_id, current_user.id, db)
    
    # Логирование в аудит
    log_action(
        AuditAction.SESSION_REVOKED,
        current_user.id,
        db,
        {"session_id": session_id, "ip_address": session.ip_address},
        request
    )
    
    return {"message": "Сессия успешно отозвана"}


@router.post("/revoke-all")
async def revoke_all_sessions(
    current_user: User = Depends(get_current_active_user),
    request: Request = None,
    db: Session = Depends(get_db)
):
    """
    Отзыв всех сессий кроме текущей
    """
    current_token_id = get_current_token_id(request, db) if request else None
    
    if not current_token_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Не удалось определить текущую сессию"
        )
    
    count = revoke_all_other_sessions(current_user.id, current_token_id, db)
    
    # Логирование в аудит
    log_action(
        AuditAction.SESSION_REVOKED,
        current_user.id,
        db,
        {"action": "revoke_all_other", "count": count},
        request
    )
    
    return {"message": f"Отозвано {count} сессий", "revoked_count": count}

