import hmac
import os
import secrets

# Единый секрет для проверки токенов, выпущенных auth-сервисом.
# Резервная генерация допустима только в development, чтобы не ломать
# локальный запуск без .env. В production SECRET_KEY обязателен.
_ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
SECRET_KEY = os.getenv("SECRET_KEY") or (
    secrets.token_hex(32) if _ENVIRONMENT != "production" else ""
)
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

# Внутренний токен для межсервисных вызовов (совместимость с auth).
INTERNAL_API_TOKEN = os.getenv("INTERNAL_API_TOKEN", "")


def check_internal_token(provided: str | None) -> None:
    """Проверяет внутренний токен; при отсутствии конфигурации запрещает доступ."""
    from fastapi import HTTPException, status

    if not INTERNAL_API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Internal API token is not configured",
        )
    if not provided or not hmac.compare_digest(provided, INTERNAL_API_TOKEN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid internal token",
        )


def role_allowed(role: str | None, allowed: tuple[str, ...]) -> bool:
    """Проверяет роль из токена auth-сервиса."""
    if not role:
        return False
    normalized = role.lower()
    return any(normalized == r.lower() for r in allowed)


# Роли, определённые в auth-сервисе.
AUTH_ROLES = ("student", "teacher", "moderator", "admin")
