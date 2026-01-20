# Примеры использования Auth Service

## 🔐 Базовые операции

### Регистрация

```bash
curl -X POST http://localhost:8002/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@college.ru",
    "password": "securepass123",
    "full_name": "Иван Иванов"
  }'
```

### Вход

```bash
curl -X POST http://localhost:8002/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@college.ru",
    "password": "securepass123"
  }'
```

### Получение информации о себе

```bash
curl -X GET http://localhost:8002/api/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Обновление токена

```bash
curl -X POST http://localhost:8002/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "YOUR_REFRESH_TOKEN"
  }'
```

### Выход

```bash
curl -X POST http://localhost:8002/api/auth/logout \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 🐍 Python примеры

### Использование с requests

```python
import requests

BASE_URL = "http://localhost:8002"

# Регистрация
response = requests.post(f"{BASE_URL}/api/auth/register", json={
    "email": "test@example.com",
    "password": "password123",
    "full_name": "Test User"
})
tokens = response.json()
access_token = tokens["access_token"]

# Использование токена
headers = {"Authorization": f"Bearer {access_token}"}
response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
user = response.json()
print(f"Привет, {user['full_name']}!")

# Обновление токена
response = requests.post(f"{BASE_URL}/api/auth/refresh", json={
    "refresh_token": tokens["refresh_token"]
})
new_tokens = response.json()
```

### Использование с httpx (async)

```python
import httpx

BASE_URL = "http://localhost:8002"

async def main():
    async with httpx.AsyncClient() as client:
        # Регистрация
        response = await client.post(f"{BASE_URL}/api/auth/register", json={
            "email": "test@example.com",
            "password": "password123",
            "full_name": "Test User"
        })
        tokens = response.json()
        
        # Использование токена
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        response = await client.get(f"{BASE_URL}/api/auth/me", headers=headers)
        user = response.json()
        print(user)

import asyncio
asyncio.run(main())
```

## 🔒 Использование в других сервисах

### Проверка токена в schedule сервисе

```python
from fastapi import Depends, HTTPException
import httpx
from typing import Optional

AUTH_SERVICE_URL = "http://backend-auth:8002"

async def verify_token_with_auth_service(token: str) -> dict:
    """Проверка токена через auth сервис"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{AUTH_SERVICE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Невалидный токен")
        return response.json()

async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    if not authorization:
        raise HTTPException(status_code=401, detail="Токен не предоставлен")
    
    token = authorization.split()[1] if " " in authorization else None
    if not token:
        raise HTTPException(status_code=401, detail="Невалидный формат токена")
    
    user_data = await verify_token_with_auth_service(token)
    # Используйте user_data для получения пользователя из вашей БД
    return user_data
```

## 🎯 Интеграция с фронтендом

### React пример

```javascript
const API_URL = 'http://localhost:8002';

// Регистрация
async function register(email, password, fullName) {
  const response = await fetch(`${API_URL}/api/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include', // Для cookies
    body: JSON.stringify({ email, password, full_name: fullName })
  });
  return response.json();
}

// Вход
async function login(email, password) {
  const response = await fetch(`${API_URL}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ email, password })
  });
  return response.json();
}

// Получение текущего пользователя
async function getMe() {
  const response = await fetch(`${API_URL}/api/auth/me`, {
    credentials: 'include'
  });
  return response.json();
}

// Обновление токена
async function refreshToken() {
  const response = await fetch(`${API_URL}/api/auth/refresh`, {
    method: 'POST',
    credentials: 'include'
  });
  return response.json();
}
```

## 🛡️ Использование ролей и разрешений

### В роутерах

```python
from fastapi import APIRouter, Depends
from dependencies import require_role, require_permission, UserRole

router = APIRouter()

# Только для админов
@router.get("/admin-panel")
async def admin_panel(user: User = Depends(require_role(UserRole.ADMIN))):
    return {"message": "Добро пожаловать в админ-панель"}

# Для админов и модераторов
@router.get("/moderation")
async def moderation(
    user: User = Depends(require_role(UserRole.ADMIN, UserRole.MODERATOR))
):
    return {"message": "Панель модерации"}

# Проверка разрешения
@router.post("/schedule/create")
async def create_schedule(
    user: User = Depends(require_permission("schedule", "create"))
):
    return {"message": "Расписание создано"}
```

## 📊 Работа с историей входов

```python
from services.user_service import get_login_history

# Получение истории входов пользователя
history = get_login_history(user_id=1, limit=50, db=db)

for entry in history:
    print(f"{entry.created_at}: {entry.status} from {entry.ip_address}")
```

## 🔧 Создание разрешений

```python
from database.models import Permission
from services.user_service import grant_permission

# Создание разрешения
permission = Permission(
    name="schedule:create",
    description="Создание расписания",
    resource="schedule",
    action="create"
)
db.add(permission)
db.commit()

# Выдача разрешения пользователю
grant_permission(user_id=1, permission_id=permission.id, db=db)
```

