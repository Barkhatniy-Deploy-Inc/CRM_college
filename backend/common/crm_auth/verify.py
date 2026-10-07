"""Проверка JWT, выпущенных auth-сервисом."""

from __future__ import annotations

from typing import Any

import jwt

from crm_auth.claims import (
    CLAIM_EMAIL,
    CLAIM_ROLE,
    CLAIM_TYPE,
    CLAIM_USER_ID,
    TOKEN_TYPE_ACCESS,
    TOKEN_TYPE_REFRESH,
)
from crm_auth.errors import TokenError, TokenExpiredError, TokenTypeError

ALGORITHM = "HS256"

# Обязательные claim'ы access-токена.
REQUIRED_ACCESS_CLAIMS = (CLAIM_USER_ID, CLAIM_EMAIL, CLAIM_ROLE)


def decode_token(token: str, secret_key: str, algorithm: str = ALGORITHM) -> dict[str, Any]:
    """Декодирует JWT и возвращает payload.

    Бросает TokenExpiredError при истечении срока и TokenError при прочих
    ошибках подписи/формата.
    """
    try:
        return jwt.decode(token, secret_key, algorithms=[algorithm])
    except jwt.ExpiredSignatureError as exc:
        raise TokenExpiredError("Токен истёк") from exc
    except jwt.InvalidTokenError as exc:
        raise TokenError("Невалидный токен") from exc


def _require_type(payload: dict[str, Any], expected: str) -> None:
    if payload.get(CLAIM_TYPE) != expected:
        raise TokenTypeError(f"Ожидался токен типа '{expected}'")


def verify_access_token(
    token: str, secret_key: str, algorithm: str = ALGORITHM
) -> dict[str, Any]:
    """Проверяет access-токен auth-сервиса и обязательные claim'ы."""
    payload = decode_token(token, secret_key, algorithm)
    _require_type(payload, TOKEN_TYPE_ACCESS)

    if not all(payload.get(claim) for claim in REQUIRED_ACCESS_CLAIMS):
        raise TokenError("Невалидные данные токена")

    return payload


def verify_refresh_token(
    token: str, secret_key: str, algorithm: str = ALGORITHM
) -> dict[str, Any]:
    """Проверяет refresh-токен auth-сервиса."""
    payload = decode_token(token, secret_key, algorithm)
    _require_type(payload, TOKEN_TYPE_REFRESH)

    if not payload.get(CLAIM_USER_ID):
        raise TokenError("Невалидные данные токена")

    return payload
