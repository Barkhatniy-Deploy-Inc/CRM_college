import os

from services.crm_common import AUTH_ROLES, role_allowed  # noqa: F401

# Единый секрет для проверки токенов, выпущенных auth-сервисом.
# В отличие от legacy-auth schedule не генерирует новый ключ: иначе он не
# сможет проверить JWT, подписанный auth-сервисом.
SECRET_KEY = os.getenv("SECRET_KEY", "")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

__all__ = ["SECRET_KEY", "ALGORITHM", "role_allowed", "AUTH_ROLES"]
