# 🔐 Auth Service - Сервис аутентификации и авторизации

Современный микросервис аутентификации и авторизации для CRM College на FastAPI.

## ✨ Особенности

- 🔑 **JWT токены** с поддержкой access и refresh токенов
- 🛡️ **Защита от брутфорса** - автоматическая блокировка после неудачных попыток
- 👥 **Система ролей** (Admin, Teacher, Student, Moderator)
- 🔐 **Разрешения (Permissions)** - детальный контроль доступа
- 📊 **История входов** - логирование всех попыток аутентификации
- ⚡ **Rate Limiting** - защита от DDoS и злоупотреблений
- 🍪 **Cookie-based auth** - поддержка токенов в cookies для веб-приложений
- 🔄 **Refresh tokens** - долгоживущие токены для обновления сессий
- 📝 **OAuth2 совместимость** - стандартный подход FastAPI

## 🏗️ Архитектура

```
backend/auth/
├── core/              # Конфигурация
│   └── config.py      # Настройки приложения
├── database/          # Работа с БД
│   ├── database.py    # Подключение к БД
│   ├── models.py       # SQLAlchemy модели
│   └── schemas.py      # Pydantic схемы
├── services/          # Бизнес-логика
│   ├── security.py    # Безопасность (JWT, пароли)
│   ├── user_service.py # Работа с пользователями
│   └── token_service.py # Работа с токенами
├── routers/           # API endpoints
│   ├── auth.py        # Аутентификация
│   └── users.py       # Управление пользователями
├── middleware/       # Middleware
│   └── rate_limit.py  # Rate limiting
└── main.py            # Точка входа
```

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Настройка переменных окружения

Создайте файл `.env`:

**Для локальной разработки (SQLite - по умолчанию):**
```env
# База данных - SQLite (локально, не требует настройки)
DB_TYPE=sqlite
SQLITE_PATH=database/auth.db

# Безопасность
SECRET_KEY=your-secret-key-here-min-32-chars
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30

# Защита от брутфорса
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=30

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:80

# Rate limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW_SECONDS=60

# Окружение
ENVIRONMENT=development
```

**Для production (PostgreSQL):**
```env
# База данных - PostgreSQL
DB_TYPE=postgresql
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=auth_db

# Остальные настройки такие же...
```

> 💡 **Примечание**: По умолчанию используется SQLite для локальной разработки. Для переключения на PostgreSQL установите `DB_TYPE=postgresql` и настройте параметры подключения.

### 3. Запуск

```bash
python main.py
```

Или через uvicorn:

```bash
uvicorn main:app --host 0.0.0.0 --port 8002 --reload
```

## 📚 API Endpoints

### Аутентификация

#### `POST /api/auth/register`
Регистрация нового пользователя

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "Иван Иванов",
  "role": "student"  // опционально
}
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 900,
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "Иван Иванов",
    "role": "student",
    "is_active": true,
    "is_verified": false
  }
}
```

#### `POST /api/auth/login`
Вход в систему

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

#### `POST /api/auth/refresh`
Обновление access токена

**Request:**
```json
{
  "refresh_token": "eyJ..."
}
```

Или через cookie: `refresh_token`

#### `POST /api/auth/logout`
Выход из системы (отзыв токенов)

#### `GET /api/auth/me`
Получение информации о текущем пользователе

#### `POST /api/auth/change-password`
Изменение пароля

**Request:**
```json
{
  "current_password": "oldpassword",
  "new_password": "newpassword123"
}
```

### Пользователи

#### `GET /api/users/me`
Информация о текущем пользователе

#### `GET /api/users/me/history`
История входов текущего пользователя

#### `PUT /api/users/me`
Обновление данных текущего пользователя

#### `GET /api/users/{user_id}`
Получение информации о пользователе (только для админов/модераторов)

#### `PUT /api/users/{user_id}`
Обновление данных пользователя (только для админов)

## 🔒 Безопасность

### Защита от брутфорса

После `MAX_LOGIN_ATTEMPTS` (по умолчанию 5) неудачных попыток входа, аккаунт блокируется на `LOCKOUT_DURATION_MINUTES` (по умолчанию 30) минут.

### Rate Limiting

По умолчанию: 100 запросов в минуту на IP адрес. Настраивается через переменные окружения.

### JWT Токены

- **Access токены**: короткоживущие (15 минут по умолчанию)
- **Refresh токены**: долгоживущие (30 дней по умолчанию), хранятся в БД
- Токены содержат: `user_id`, `email`, `role`

## 👥 Роли и разрешения

### Роли

- `admin` - полный доступ
- `moderator` - модерация контента
- `teacher` - преподаватель
- `student` - студент

### Использование в коде

```python
from dependencies import require_role, require_permission, UserRole

# Проверка роли
@router.get("/admin-only")
async def admin_endpoint(user: User = Depends(require_role(UserRole.ADMIN))):
    ...

# Проверка разрешения
@router.post("/create-schedule")
async def create_schedule(
    user: User = Depends(require_permission("schedule", "create"))
):
    ...
```

## 🐳 Docker

```bash
docker build -t auth-service .
docker run -p 8002:8002 --env-file .env auth-service
```

## 📊 База данных

### Поддержка SQLite и PostgreSQL

Сервис поддерживает два типа БД:

- **SQLite** (по умолчанию) - для локальной разработки, не требует настройки
- **PostgreSQL** - для production, настраивается через переменные окружения

### Переключение между БД

**SQLite (локально):**
```env
DB_TYPE=sqlite
SQLITE_PATH=database/auth.db
```

**PostgreSQL (production):**
```env
DB_TYPE=postgresql
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=auth_db
```

### Модели

- **User** - пользователи
- **RefreshToken** - refresh токены
- **LoginHistory** - история входов
- **Permission** - разрешения
- **UserPermission** - связь пользователей и разрешений

### Миграции

Используйте Alembic для миграций (можно добавить позже):

```bash
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## 🧪 Тестирование

```bash
pytest tests/
```

## 📝 Примеры использования

### Регистрация и вход

```python
import requests

# Регистрация
response = requests.post("http://localhost:8002/api/auth/register", json={
    "email": "test@example.com",
    "password": "password123",
    "full_name": "Test User"
})
tokens = response.json()

# Использование токена
headers = {"Authorization": f"Bearer {tokens['access_token']}"}
response = requests.get("http://localhost:8002/api/auth/me", headers=headers)
```

### Обновление токена

```python
# Когда access токен истек
response = requests.post("http://localhost:8002/api/auth/refresh", json={
    "refresh_token": tokens['refresh_token']
})
new_tokens = response.json()
```

## 🔧 Конфигурация

Все настройки находятся в `core/config.py` и настраиваются через переменные окружения.

## 📦 Зависимости

- FastAPI - веб-фреймворк
- SQLAlchemy - ORM
- PyJWT - JWT токены
- passlib - хеширование паролей
- pydantic - валидация данных
- psycopg - драйвер PostgreSQL

## 🤝 Интеграция с другими сервисами

Другие сервисы могут проверять токены через:

1. **Прямая проверка JWT** (если знают SECRET_KEY)
2. **HTTP запрос к `/api/auth/me`** с токеном
3. **Выделенный endpoint для валидации токенов** (можно добавить)

## 📄 Лицензия

Внутренний проект CRM College

