# 🧪 Руководство по тестированию CRM_college

## 📋 Содержание
1. [Быстрый старт](#быстрый-старт)
2. [Локальное тестирование](#локальное-тестирование)
3. [Docker тестирование](#docker-тестирование)
4. [API тестирование](#api-тестирование)
5. [Автоматические тесты](#автоматические-тесты)
6. [Нагрузочное тестирование](#нагрузочное-тестирование)
7. [Мониторинг и логи](#мониторинг-и-логи)

---

## 🚀 Быстрый старт

### Предварительные требования
```bash
# Установите необходимые инструменты
pip install httpx pytest pytest-asyncio
npm install -g newman  # Для Postman коллекций
```

### Проверка health endpoints
```bash
# Auth сервис
curl http://localhost:8002/api/health

# Schedule сервис  
curl http://localhost:8000/api/health

# Techcard сервис
curl http://localhost:8001/api/health
```

---

## 🏠 Локальное тестирование

### 1. Настройка окружения

#### Создайте .env файлы для каждого сервиса:

**backend/auth/.env:**
```env
DB_HOST=localhost
DB_PORT=5432
AUTH_DB_NAME=auth_db
DB_USER=postgres
DB_PASSWORD=your_password
SECRET_KEY=your-super-secret-key-min-32-chars
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080
ENVIRONMENT=development
DEBUG=true
```

**backend/schedule/.env:**
```env
DB_HOST=localhost
DB_PORT=5432
SCHEDULE_DB_NAME=schedule_db
DB_USER=postgres
DB_PASSWORD=your_password
SECRET_KEY=your-super-secret-key-min-32-chars
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080
AUTH_SERVICE_URL=http://localhost:8002
ENVIRONMENT=development
DEBUG=true
```

### 2. Запуск сервисов локально

```bash
# Терминал 1 - Auth сервис
cd backend/auth
pip install -r requirements.txt
python main.py

# Терминал 2 - Schedule сервис
cd backend/schedule
pip install -r requirements.txt
python main.py

# Терминал 3 - Techcard сервис
cd backend/techcard
pip install -r requirements.txt
python main.py
```

### 3. Проверка запуска
```bash
# Проверяем все сервисы
curl http://localhost:8002/api/health  # Auth
curl http://localhost:8000/api/health  # Schedule
curl http://localhost:8001/api/health  # Techcard
```

---

## 🐳 Docker тестирование

### 1. Сборка и запуск через Docker Compose

```bash
# Клонируйте проект
git clone https://github.com/Barkhatniy-Deploy-Inc/CRM_college.git
cd CRM_college

# Создайте .env файл в корне проекта
cat > .env << EOF
DB_HOST=your-postgres-host
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your-secure-password
AUTH_DB_NAME=auth_db
SCHEDULE_DB_NAME=schedule_db
TECHCARD_DB_NAME=techcard_db
SECRET_KEY=your-super-secret-key-min-32-chars-long
ALLOWED_ORIGINS=http://localhost:3000,http://localhost
EOF

# Запуск для разработки
docker-compose -f docker-compose.dev.yml up --build

# Или для тестирования
docker-compose -f docker-compose.test.yml up --build
```

### 2. Проверка контейнеров
```bash
# Проверяем статус контейнеров
docker-compose ps

# Проверяем логи
docker-compose logs backend-auth
docker-compose logs backend-schedule
docker-compose logs backend-techcard

# Проверяем health endpoints
curl http://localhost:8002/api/health
curl http://localhost:8000/api/health
curl http://localhost:8001/api/health
```

---

## 🔌 API тестирование

### 1. Тестирование Auth сервиса

#### Регистрация пользователя:
```bash
curl -X POST http://localhost:8002/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123",
    "full_name": "Test User"
  }'
```

#### Вход в систему:
```bash
curl -X POST http://localhost:8002/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123"
  }'
```

#### Получение профиля:
```bash
# Сохраните токен из ответа login
TOKEN="your-jwt-token-here"

curl -X GET http://localhost:8002/api/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

### 2. Тестирование Schedule сервиса

#### Получение курсов:
```bash
curl -X GET http://localhost:8000/api/courses
```

#### Создание курса (требует авторизации):
```bash
curl -X POST http://localhost:8000/api/courses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "Тестовый курс",
    "description": "Описание тестового курса"
  }'
```

#### Получение расписания:
```bash
curl -X GET "http://localhost:8000/api/schedule?limit=10"
```

### 3. Тестирование Techcard сервиса

#### Получение техкарт:
```bash
curl -X GET http://localhost:8001/api/techcards
```

#### Создание техкарты:
```bash
curl -X POST http://localhost:8001/api/techcards \
  -H "Content-Type: application/json" \
  -d '{
    "tema": "Тестовая тема урока",
    "group_id": 1,
    "lesson_id": 1,
    "teacher_id": 1
  }'
```

---

## 🧪 Автоматические тесты

### 1. Создание тестового окружения

Создайте файл `tests/conftest.py`:
```python
import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient

# Импортируйте ваши приложения
from backend.auth.main import app as auth_app
from backend.schedule.main import app as schedule_app
from backend.techcard.main import app as techcard_app

@pytest.fixture
def auth_client():
    return TestClient(auth_app)

@pytest.fixture
def schedule_client():
    return TestClient(schedule_app)

@pytest.fixture
def techcard_client():
    return TestClient(techcard_app)

@pytest.fixture
async def async_auth_client():
    async with AsyncClient(app=auth_app, base_url="http://test") as client:
        yield client
```

### 2. Тесты для Auth сервиса

Создайте файл `tests/test_auth.py`:
```python
import pytest
from fastapi.testclient import TestClient

def test_health_check(auth_client):
    response = auth_client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_register_user(auth_client):
    user_data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User"
    }
    response = auth_client.post("/api/auth/register", json=user_data)
    assert response.status_code == 201
    assert "access_token" in response.json()

def test_login_user(auth_client):
    # Сначала регистрируем пользователя
    user_data = {
        "email": "test2@example.com",
        "password": "testpassword123",
        "full_name": "Test User 2"
    }
    auth_client.post("/api/auth/register", json=user_data)
    
    # Затем логинимся
    login_data = {
        "email": "test2@example.com",
        "password": "testpassword123"
    }
    response = auth_client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
```

### 3. Запуск тестов

```bash
# Установите pytest
pip install pytest pytest-asyncio httpx

# Запустите тесты
pytest tests/ -v

# Запуск с покрытием кода
pip install pytest-cov
pytest tests/ --cov=backend --cov-report=html
```

---

## ⚡ Нагрузочное тестирование

### 1. Использование Apache Bench (ab)

```bash
# Установка (Ubuntu/Debian)
sudo apt-get install apache2-utils

# Тест health endpoint (100 запросов, 10 одновременно)
ab -n 100 -c 10 http://localhost:8002/api/health

# Тест с POST запросом
ab -n 50 -c 5 -p login_data.json -T application/json http://localhost:8002/api/auth/login
```

### 2. Использование wrk

```bash
# Установка wrk
sudo apt-get install wrk

# Простой тест
wrk -t12 -c400 -d30s http://localhost:8000/api/courses

# Тест с POST запросом
wrk -t12 -c400 -d30s -s post.lua http://localhost:8002/api/auth/login
```

### 3. Использование Python locust

```python
# locustfile.py
from locust import HttpUser, task, between

class CRMUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Регистрация и логин
        self.client.post("/api/auth/register", json={
            "email": f"user{self.environment.runner.user_count}@test.com",
            "password": "testpass123",
            "full_name": "Test User"
        })
        
        response = self.client.post("/api/auth/login", json={
            "email": f"user{self.environment.runner.user_count}@test.com",
            "password": "testpass123"
        })
        
        if response.status_code == 200:
            self.token = response.json()["access_token"]
    
    @task(3)
    def get_courses(self):
        self.client.get("/api/courses")
    
    @task(1)
    def get_schedule(self):
        self.client.get("/api/schedule")
    
    @task(1)
    def health_check(self):
        self.client.get("/api/health")

# Запуск: locust -f locustfile.py --host=http://localhost:8000
```

---

## 📊 Мониторинг и логи

### 1. Просмотр логов Docker

```bash
# Логи всех сервисов
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs -f backend-auth
docker-compose logs -f backend-schedule
docker-compose logs -f backend-techcard

# Последние 100 строк логов
docker-compose logs --tail=100 backend-auth
```

### 2. Мониторинг ресурсов

```bash
# Использование ресурсов контейнерами
docker stats

# Детальная информация о контейнере
docker inspect crm_college_backend-auth_1
```

### 3. Проверка базы данных

```bash
# Подключение к PostgreSQL
psql -h localhost -p 5432 -U postgres -d auth_db

# Проверка таблиц
\dt

# Проверка пользователей
SELECT * FROM users LIMIT 5;
```

---

## 🔧 Отладка проблем

### Частые проблемы и решения:

#### 1. Сервис не запускается
```bash
# Проверьте логи
docker-compose logs backend-auth

# Проверьте переменные окружения
docker-compose exec backend-auth env | grep DB_

# Проверьте подключение к БД
docker-compose exec backend-auth python -c "
from database.database import engine
print(engine.url)
"
```

#### 2. Ошибки авторизации
```bash
# Проверьте SECRET_KEY
echo $SECRET_KEY

# Проверьте токен
curl -X POST http://localhost:8002/api/auth/validate \
  -H "Authorization: Bearer $TOKEN"
```

#### 3. Проблемы с CORS
```bash
# Проверьте ALLOWED_ORIGINS
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: X-Requested-With" \
     -X OPTIONS \
     http://localhost:8002/api/auth/login
```

---

## 📝 Чек-лист тестирования

### ✅ Базовые проверки:
- [ ] Все сервисы запускаются без ошибок
- [ ] Health endpoints отвечают 200 OK
- [ ] База данных подключается
- [ ] Логи не содержат критических ошибок

### ✅ Функциональные тесты:
- [ ] Регистрация пользователя работает
- [ ] Авторизация работает
- [ ] JWT токены валидируются
- [ ] CRUD операции работают
- [ ] Межсервисное взаимодействие работает

### ✅ Нагрузочные тесты:
- [ ] Сервисы выдерживают 100 одновременных запросов
- [ ] Время ответа < 500ms для простых запросов
- [ ] Нет утечек памяти при длительной работе

### ✅ Безопасность:
- [ ] Пароли хешируются
- [ ] JWT токены имеют срок действия
- [ ] CORS настроен правильно
- [ ] Нет SQL инъекций

---

## 🚀 Автоматизация тестирования

### GitHub Actions workflow (.github/workflows/test.yml):
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: testpass
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r backend/auth/requirements.txt
        pip install pytest pytest-asyncio httpx
    
    - name: Run tests
      env:
        DB_HOST: localhost
        DB_PASSWORD: testpass
        SECRET_KEY: test-secret-key-for-testing-only
      run: |
        pytest tests/ -v
```

---

## 📞 Поддержка

Если у вас возникли проблемы с тестированием:

1. Проверьте логи сервисов
2. Убедитесь, что все переменные окружения настроены
3. Проверьте подключение к базе данных
4. Обратитесь к документации API (Swagger UI доступен по адресам):
   - Auth: http://localhost:8002/docs
   - Schedule: http://localhost:8000/docs  
   - Techcard: http://localhost:8001/docs

---

**Удачного тестирования! 🎉**