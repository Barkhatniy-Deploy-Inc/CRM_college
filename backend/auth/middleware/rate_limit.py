from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
from collections import defaultdict, deque

from core.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware для ограничения частоты запросов"""
    
    def __init__(self, app, requests_per_window: int = None, window_seconds: int = None):
        super().__init__(app)
        self.requests_per_window = requests_per_window or settings.RATE_LIMIT_REQUESTS
        self.window_seconds = window_seconds or settings.RATE_LIMIT_WINDOW_SECONDS
        self.requests: dict[str, deque[float]] = defaultdict(deque)
        self._request_count = 0
    
    async def dispatch(self, request: Request, call_next):
        if not settings.RATE_LIMIT_ENABLED:
            return await call_next(request)
        
        # Получаем IP адрес клиента
        client_ip = get_client_ip(request)
        
        # Очистка старых записей
        current_time = time.time()
        client_requests = self.requests[client_ip]
        while client_requests and current_time - client_requests[0] >= self.window_seconds:
            client_requests.popleft()

        # Remove idle clients periodically so arbitrary source addresses cannot
        # grow the in-process rate-limit table forever.
        self._request_count += 1
        if self._request_count % 256 == 0:
            cutoff = current_time - self.window_seconds
            for ip, timestamps in tuple(self.requests.items()):
                if ip == client_ip:
                    continue
                while timestamps and timestamps[0] < cutoff:
                    timestamps.popleft()
                if not timestamps:
                    self.requests.pop(ip, None)
        
        # Проверка лимита
        if len(client_requests) >= self.requests_per_window:
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
        client_requests.append(current_time)
        
        # Выполняем запрос
        response = await call_next(request)
        
        # Добавляем заголовки rate limit
        remaining = self.requests_per_window - len(client_requests)
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
