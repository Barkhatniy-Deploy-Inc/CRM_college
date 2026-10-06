import os

# Единый секрет для проверки токенов, выпущенных auth-сервисом.
# В отличие от legacy-auth schedule не генерирует новый ключ: иначе он не
# сможет проверить JWT, подписанный auth-сервисом.
SECRET_KEY = os.getenv("SECRET_KEY", "")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")


def role_allowed(role: str | None, allowed: tuple[str, ...]) -> bool:
    """Проверяет роль из токена auth-сервиса."""
    if not role:
        return False
    normalized = role.lower()
    return any(normalized == r.lower() for r in allowed)


# Роли, определённые в auth-сервисе.
AUTH_ROLES = ("student", "teacher", "moderator", "admin")
