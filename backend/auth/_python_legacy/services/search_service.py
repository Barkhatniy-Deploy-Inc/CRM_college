"""Сервис для поиска и фильтрации пользователей"""
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc
from typing import Tuple, List
from math import ceil

from database.models import User, UserRole
from database.schemas import UserPublic, UserSearchParams, UserListResponse


def search_users(params: UserSearchParams, db: Session) -> UserListResponse:
    """
    Поиск и фильтрация пользователей с пагинацией
    
    Args:
        params: Параметры поиска
        db: Сессия БД
    
    Returns:
        Список пользователей с метаданными пагинации
    """
    query = db.query(User)
    
    # Поиск по email или имени
    if params.search:
        search_term = f"%{params.search.lower()}%"
        query = query.filter(
            or_(
                User.email.ilike(search_term),
                User.full_name.ilike(search_term)
            )
        )
    
    # Фильтр по роли
    if params.role:
        query = query.filter(User.role == params.role)
    
    # Фильтр по активности
    if params.is_active is not None:
        query = query.filter(User.is_active == params.is_active)
    
    # Фильтр по верификации
    if params.is_verified is not None:
        query = query.filter(User.is_verified == params.is_verified)
    
    # Подсчет общего количества
    total = query.count()
    
    # Сортировка
    sort_column = getattr(User, params.sort, User.created_at)
    if params.order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))
    
    # Пагинация
    offset = (params.page - 1) * params.limit
    users = query.offset(offset).limit(params.limit).all()
    
    # Вычисление количества страниц
    pages = ceil(total / params.limit) if total > 0 else 0
    
    return UserListResponse(
        users=[UserPublic.model_validate(user) for user in users],
        total=total,
        page=params.page,
        limit=params.limit,
        pages=pages
    )

