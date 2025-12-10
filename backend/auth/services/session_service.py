"""Сервис для управления сессиями пользователей"""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import HTTPException, status

from database.models import RefreshToken, User
from database.schemas import SessionResponse, SessionUpdate


def get_user_sessions(user_id: int, current_token_id: Optional[int], db: Session) -> List[SessionResponse]:
    """
    Получение всех активных сессий пользователя
    
    Args:
        user_id: ID пользователя
        current_token_id: ID текущей сессии (для пометки is_current)
        db: Сессия БД
    """
    sessions = db.query(RefreshToken).filter(
        and_(
            RefreshToken.user_id == user_id,
            RefreshToken.is_revoked == False,
            RefreshToken.expires_at > datetime.now(timezone.utc)
        )
    ).order_by(RefreshToken.last_used_at.desc().nullslast(), RefreshToken.created_at.desc()).all()
    
    result = []
    for session in sessions:
        session_dict = {
            "id": session.id,
            "ip_address": session.ip_address,
            "user_agent": session.user_agent,
            "device_name": session.device_name,
            "created_at": session.created_at,
            "last_used_at": session.last_used_at,
            "expires_at": session.expires_at,
            "is_current": session.id == current_token_id if current_token_id else False
        }
        result.append(SessionResponse(**session_dict))
    
    return result


def update_session_device_name(session_id: int, user_id: int, device_name: str, db: Session) -> RefreshToken:
    """
    Обновление имени устройства для сессии
    
    Args:
        session_id: ID сессии
        user_id: ID пользователя (для проверки владельца)
        device_name: Новое имя устройства
        db: Сессия БД
    """
    session = db.query(RefreshToken).filter(
        and_(
            RefreshToken.id == session_id,
            RefreshToken.user_id == user_id,
            RefreshToken.is_revoked == False
        )
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сессия не найдена"
        )
    
    session.device_name = device_name
    db.commit()
    db.refresh(session)
    
    return session


def revoke_session(session_id: int, user_id: int, db: Session) -> None:
    """
    Отзыв конкретной сессии
    
    Args:
        session_id: ID сессии
        user_id: ID пользователя (для проверки владельца)
        db: Сессия БД
    """
    session = db.query(RefreshToken).filter(
        and_(
            RefreshToken.id == session_id,
            RefreshToken.user_id == user_id
        )
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сессия не найдена"
        )
    
    session.is_revoked = True
    db.commit()


def revoke_all_other_sessions(user_id: int, current_token_id: int, db: Session) -> int:
    """
    Отзыв всех сессий кроме текущей
    
    Args:
        user_id: ID пользователя
        current_token_id: ID текущей сессии (не отзывать)
        db: Сессия БД
    
    Returns:
        Количество отозванных сессий
    """
    count = db.query(RefreshToken).filter(
        and_(
            RefreshToken.user_id == user_id,
            RefreshToken.id != current_token_id,
            RefreshToken.is_revoked == False
        )
    ).update({"is_revoked": True})
    
    db.commit()
    return count


def update_session_last_used(token: str, db: Session) -> None:
    """
    Обновление времени последнего использования сессии
    
    Args:
        token: Refresh токен
        db: Сессия БД
    """
    session = db.query(RefreshToken).filter(RefreshToken.token == token).first()
    if session:
        session.last_used_at = datetime.now(timezone.utc)
        db.commit()

