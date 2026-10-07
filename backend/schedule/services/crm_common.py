"""Bootstrap общего пакета crm_auth для schedule-сервиса.

Пробрасывает единый контракт из backend/common в schedule.
"""

from __future__ import annotations

import os
import sys

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_BACKEND_DIR = os.path.dirname(os.path.dirname(_THIS_DIR))
_COMMON_DIR = os.path.join(_BACKEND_DIR, "common")

if _COMMON_DIR not in sys.path:
    sys.path.insert(0, _COMMON_DIR)

from crm_auth import (  # noqa: E402,F401
    AUTH_ROLES,
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
    "TokenError",
    "TokenExpiredError",
    "TokenTypeError",
    "decode_token",
    "role_allowed",
    "verify_access_token",
    "verify_refresh_token",
]
