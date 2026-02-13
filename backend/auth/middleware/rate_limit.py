from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from typing import Dict, Tuple
from datetime import datetime, timedelta
import time
from collections import defaultdict

from core.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware для ограничения частоты запросов"""
    
    def __init__(self, app, requests_per_window: int = None, window_seconds: int = None):
        super().__init__(app)
        self.requests_per_window = requests_per_window or settings.RATE_LIMIT_REQUESTS
        self.window_seconds = window_seconds or settings.RATE_LIMIT_WINDOW_SECONDS
        self.requests: Dict[str, list] = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next):
        if not settings.RATE_LIMIT_ENABLED:
            return await call_next(request)
        
        # Получаем IP адрес клиента
        client_ip = request.client.host if request.client else "unknown"
        
        # Очистка старых записей
        current_time = time.time()
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if current_time - req_time < self.window_seconds
        ]
        
        # Проверка лимита
        if len(self.requests[client_ip]) >= self.requests_per_window:
            return Response(
                content="Превышен лимит запросов. Попробуйте позже.",
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                headers={
                    "Retry-After": str(self.window_seconds),
                    "X-RateLimit-Limit": str(self.requests_per_window),
                    "X-RateLimit-Remaining": "0"
                }
            )
        
        # Добавляем текущий запрос
        self.requests[client_ip].append(current_time)
        
        # Выполняем запрос
        response = await call_next(request)
        
        # Добавляем заголовки rate limit
        remaining = self.requests_per_window - len(self.requests[client_ip])
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_window)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(current_time + self.window_seconds))
        
        return response


def get_client_ip(request: Request) -> str:
    """Получение IP адреса клиента с учетом прокси"""
    # В первую очередь проверяем X-Real-IP, так как он устанавливается Nginx
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Если X-Real-IP нет, берем последний адрес из X-Forwarded-For (ближайший к нам прокси)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[-1].strip()
    
    return request.client.host if request.client else "unknown"


def get_user_agent(request: Request) -> str:
    """Получение User-Agent"""
    return request.headers.get("User-Agent", "unknown")

