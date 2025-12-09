"""
Auth Middleware для проверки токенов через Auth Service
"""

import httpx
from fastapi import HTTPException, Request
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class AuthMiddleware:
    def __init__(self, auth_service_url: str = "http://localhost:8002"):
        self.auth_service_url = auth_service_url.rstrip('/')
        
    async def validate_token(self, authorization: Optional[str] = None, access_token: Optional[str] = None):
        """Валидация токена через Auth Service"""
        try:
            async with httpx.AsyncClient() as client:
                headers = {}
                cookies = {}
                
                if authorization:
                    headers["Authorization"] = authorization
                if access_token:
                    cookies["access_token"] = access_token
                
                response = await client.post(
                    f"{self.auth_service_url}/api/auth/validate",
                    headers=headers,
                    cookies=cookies,
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"Auth service returned {response.status_code}: {response.text}")
                    return None
                    
        except httpx.TimeoutException:
            logger.error("Auth service timeout")
            return None
        except Exception as e:
            logger.error(f"Error validating token with auth service: {e}")
            return None

async def get_current_user_from_auth_service(request: Request):
    """Dependency для получения текущего пользователя через Auth Service"""
    auth_middleware = AuthMiddleware()
    
    # Получаем токен из заголовка или cookie
    authorization = request.headers.get("Authorization")
    access_token = request.cookies.get("access_token")
    
    if not authorization and not access_token:
        raise HTTPException(
            status_code=401,
            detail="Токен авторизации не предоставлен",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Валидируем токен через Auth Service
    validation_result = await auth_middleware.validate_token(authorization, access_token)
    
    if not validation_result or not validation_result.get("valid"):
        raise HTTPException(
            status_code=401,
            detail="Невалидный или истекший токен",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return validation_result.get("user")