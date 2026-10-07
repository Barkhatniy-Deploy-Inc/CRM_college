"""Bootstrap общего пакета crm_auth для backend-сервисов.

Добавляет каталог `backend/common` в sys.path и реэкспортирует ключевые
функции проверки JWT. Импортируйте этот модуль в начале пакета сервиса:

    from crm_common import verify_access_token, role_allowed
"""

from __future__ import annotations

import os
import sys

# backend/common относительно backend/<service>/core/crm_common.py
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_BACKEND_DIR = os.path.dirname(os.path.dirname(_THIS_DIR))
_COMMON_DIR = os.path.join(_BACKEND_DIR, "common")

if _COMMON_DIR not in sys.path:
    sys.path.insert(0, _COMMON_DIR)

from crm_auth import (  # noqa: E402,F401
    AUTH_ROLES,
    CLAIM_EMAIL,
    CLAIM_ROLE,
    CLAIM_TYPE,
    CLAIM_USER_ID,
    TOKEN_TYPE_ACCESS,
    TOKEN_TYPE_REFRESH,
    TokenError,
    TokenExpiredError,
    TokenTypeError,
    decode_token,
    role_allowed,
    verify_access_token,
    verify_refresh_token,
)

__all__ = [
    "AUTH_ROLES",
    "CLAIM_EMAIL",
    "CLAIM_ROLE",
    "CLAIM_TYPE",
    "CLAIM_USER_ID",
    "TOKEN_TYPE_ACCESS",
    "TOKEN_TYPE_REFRESH",
    "TokenError",
    "TokenExpiredError",
    "TokenTypeError",
    "decode_token",
    "role_allowed",
    "verify_access_token",
    "verify_refresh_token",
]
