from fastapi import Depends, HTTPException, Header, Cookie, status
from typing import Optional

from services.tokens import SECRET_KEY, ALGORITHM, role_allowed

import jwt


def _decode(token: str) -> dict:
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

    # Принимаем только access-токены auth-сервиса, не refresh.
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


async def get_current_user(
    authorization: Optional[str] = Header(None),
    access_token: Optional[str] = Cookie(None),
) -> dict:
    """Валидирует access-токен, выпущенный auth-сервисом (cookie или Bearer)."""
    token = access_token
    if not token and authorization and " " in authorization:
        token = authorization.split()[1]
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Не аутентифицирован")
    return _decode(token)


async def get_current_active_user(current_user: dict = Depends(get_current_user)) -> dict:
    return current_user


def require_roles(*roles: str):
    """Зависимость: доступ только для указанных ролей (из токена auth)."""

    async def checker(current_user: dict = Depends(get_current_user)) -> dict:
        if not role_allowed(current_user.get("role"), roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав",
            )
        return current_user

    return checker
