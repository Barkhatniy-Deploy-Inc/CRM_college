"""Общий контракт аутентификации CRM College.

Пакет используется всеми backend-сервисами (auth, schedule, techcard), чтобы
не дублировать логику выпуска и проверки JWT.

Содержит:
- `claims` — единые имена claim'ов и значения `type`;
- `verify` — проверка access/refresh токенов, выпущенных auth-сервисом;
- `roles` — работа с ролями из токена.

Пакет не зависит от FastAPI и ORM конкретного сервиса.
"""

from crm_auth.claims import (
    CLAIM_EMAIL,
    CLAIM_EXP,
    CLAIM_ROLE,
    CLAIM_TYPE,
    CLAIM_USER_ID,
    TOKEN_TYPE_ACCESS,
    TOKEN_TYPE_REFRESH,
)
from crm_auth.errors import TokenError, TokenExpiredError, TokenTypeError
from crm_auth.roles import AUTH_ROLES, role_allowed
from crm_auth.verify import decode_token, verify_access_token, verify_refresh_token

__all__ = [
    "CLAIM_EMAIL",
    "CLAIM_EXP",
    "CLAIM_ROLE",
    "CLAIM_TYPE",
    "CLAIM_USER_ID",
    "TOKEN_TYPE_ACCESS",
    "TOKEN_TYPE_REFRESH",
    "TokenError",
    "TokenExpiredError",
    "TokenTypeError",
    "AUTH_ROLES",
    "role_allowed",
    "decode_token",
    "verify_access_token",
    "verify_refresh_token",
]
