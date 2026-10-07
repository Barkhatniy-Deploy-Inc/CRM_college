"""Проверка JWT, выпущенных auth-сервисом.

Единый контракт вынесен в пакет backend/common (crm_auth).
"""

import os
from typing import Optional

from fastapi import Cookie, Header, HTTPException, status

from crm_common import (
    TokenError,
    TokenExpiredError,
    TokenTypeError,
    verify_access_token,
)

SECRET_KEY = os.getenv("SECRET_KEY", "")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")


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
        return verify_access_token(token, SECRET_KEY, ALGORITHM)
    except TokenExpiredError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Токен истёк")
    except TokenTypeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный тип токена",
        )
    except TokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный токен",
        )
