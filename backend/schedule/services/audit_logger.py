import httpx
import logging
import os
from typing import Optional, Dict, Any

# URL сервиса авторизации для записи логов
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth:8000").rstrip("/")
AUDIT_URL = f"{AUTH_SERVICE_URL}/api/users/audit-log/internal"
INTERNAL_API_TOKEN = os.getenv("INTERNAL_API_TOKEN", "")

logger = logging.getLogger("schedule_audit")

async def log_schedule_action(
    action: str,
    user_id: Optional[int],
    details: Optional[Dict[str, Any]] = None
):
    """
    Отправляет лог в централизованный сервис аудита (Auth Service)
    """
    payload = {
        "action": action,
        "user_id": user_id,
        "details": details or {}
    }
    headers = {"X-Internal-Token": INTERNAL_API_TOKEN} if INTERNAL_API_TOKEN else {}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(AUDIT_URL, json=payload, headers=headers, timeout=2.0)
            if response.status_code != 201:
                logger.error(f"Failed to send audit log: {response.text}")
    except Exception as e:
        logger.error(f"Error connecting to Audit service: {str(e)}")
