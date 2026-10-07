"""Роли и проверка прав по роли из токена."""

# Роли, определённые в auth-сервисе.
AUTH_ROLES = ("student", "teacher", "moderator", "admin")


def role_allowed(role: str | None, allowed: tuple[str, ...]) -> bool:
    """Проверяет, входит ли роль в список разрешённых (без учёта регистра)."""
    if not role:
        return False
    normalized = role.lower()
    return any(normalized == item.lower() for item in allowed)
