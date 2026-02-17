import httpx
import logging
from typing import Optional, Dict, Any

# URL сервиса авторизации для записи логов
AUTH_SERVICE_URL = "http://auth:8000/api/users/audit-log/internal"

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
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(AUTH_SERVICE_URL, json=payload, timeout=2.0)
            if response.status_code != 201:
                logger.error(f"Failed to send audit log: {response.text}")
    except Exception as e:
        logger.error(f"Error connecting to Audit service: {str(e)}")
