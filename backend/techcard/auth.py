"""Проверка JWT, выпущенных auth-сервисом.

Временная реализация до перехода на единый модуль авторизации
(см. docs/EPIC_RESTRUCTURE.md, CRM-10).
"""

import os
from typing import Optional

import jwt
from fastapi import Cookie, Header, HTTPException, status

SECRET_KEY = os.getenv("SECRET_KEY", "")
ALGORITHM = "HS256"


async def get_current_user(
    authorization: Optional[str] = Header(None),
    access_token: Optional[str] = Cookie(None),
) -> dict:
    """Достаёт и проверяет access-токен auth-сервиса (cookie или Bearer)."""
    token = access_token
    if not token and authorization and " " in authorization:
        token = authorization.split()[1]

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не аутентифицирован",
        )
    if not SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="SECRET_KEY не сконфигурирован",
        )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Токен истёк")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Невалидный токен")

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный тип токена",
        )
    if not all(payload.get(claim) for claim in ("user_id", "email", "role")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидные данные токена",
        )

    return payload
