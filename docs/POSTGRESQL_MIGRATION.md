# 🐘 PostgreSQL Migration Guide

## ✅ **ВЫПОЛНЕННЫЕ ИЗМЕНЕНИЯ:**

### 1. **Удален локальный PostgreSQL контейнер**
- **Файл**: `docker-compose.yml`
- **Изменение**: Удален сервис `db` и зависимости от него
- **Причина**: Используется внешний PostgreSQL сервер

### 2. **Настроен techcard сервис для PostgreSQL**
- **Файл**: `backend/techcard/database/dependencies.py`
- **Изменение**: Заменен SQLite на PostgreSQL подключение
- **Конфигурация**: Использует переменные окружения для подключения
- **База данных**: `techcard_db`

### 3. **Добавлен psycopg2 для techcard сервиса**
- **Файл**: `backend/techcard/requirements.txt`
- **Добавлено**: `psycopg2-binary==2.9.9`
- **Назначение**: PostgreSQL драйвер для Python

### 4. **Обновлен docker-compose.yml**
- **Auth сервис**: Использует `auth_db`
- **Schedule сервис**: Использует `schedule_db`
- **Techcard сервис**: Использует `techcard_db`
- **Переменные окружения**: Настроены для внешнего PostgreSQL

### 5. **Создан SQL скрипт инициализации**
- **Файл**: `init_auth_db.sql`
- **Функции**: 
  - Создание `auth_db` и `techcard_db`
  - Настройка расширений (uuid-ossp, pgcrypto)
  - Создание схем и прав доступа

### 6. **Обновлен .env.example**
- **Добавлено**: `TECHCARD_DB_NAME=techcard_db`
- **Настройка**: Конфигурация для внешнего PostgreSQL сервера

## 🗄️ **СТРУКТУРА БАЗ ДАННЫХ:**

### PostgreSQL Сервер содержит:
```
├── auth_db          # База данных для auth сервиса
│   ├── public       # Основная схема
│   └── auth         # Дополнительная схема (опционально)
├── schedule_db      # База данных для schedule сервиса  
│   ├── public       # Основная схема
│   └── schedule     # Дополнительная схема (опционально)
└── techcard_db      # База данных для techcard сервиса
    ├── public       # Основная схема
    └── techcard     # Дополнительная схема (опционально)
```

## 🔧 **ИНСТРУКЦИИ ПО РАЗВЕРТЫВАНИЮ:**

### 1. **Инициализация PostgreSQL сервера**
```bash
# Подключение к PostgreSQL как суперпользователь
psql -U postgres -h your-postgres-server.com

# Выполнение скрипта инициализации
\i init_auth_db.sql
```

### 2. **Настройка переменных окружения**
```bash
# Создание .env файла на основе .env.example
cp .env.example .env

# Редактирование .env файла
nano .env
```

### 3. **Обязательные переменные окружения:**
```env
# PostgreSQL Configuration
DB_HOST=your-postgres-server.com
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_secure_password

# Database Names
AUTH_DB_NAME=auth_db
DB_NAME=schedule_db
TECHCARD_DB_NAME=techcard_db

# Security
SECRET_KEY=your-super-secret-jwt-key-here

# CORS
ALLOWED_ORIGINS=http://localhost:3000,https://your-domain.com
```

### 4. **Запуск проекта**
```bash
# Запуск всех сервисов
docker compose up --build -d

# Проверка статуса
docker compose ps

# Просмотр логов
docker compose logs -f
```

## 🔍 **ПРОВЕРКА РАБОТОСПОСОБНОСТИ:**

### Health Check Endpoints:
```bash
# Frontend
curl http://localhost/

# API Gateway Health
curl http://localhost/api/health

# Auth Service (через nginx)
curl http://localhost/api/auth/health

# Schedule Service (через nginx)  
curl http://localhost/api/schedule/health

# Techcard Service (через nginx)
curl http://localhost/api/techcard/health
```

### Прямые подключения к сервисам:
```bash
# Auth Service (прямое подключение)
curl http://localhost:8002/api/health

# Schedule Service (прямое подключение)
curl http://localhost:8000/api/health

# Techcard Service (прямое подключение)
curl http://localhost:8001/api/health
```

## 🚨 **ВАЖНЫЕ ЗАМЕЧАНИЯ:**

### 1. **Безопасность**
- ⚠️ Измените `SECRET_KEY` в production
- ⚠️ Используйте сильные пароли для PostgreSQL
- ⚠️ Настройте правильные `ALLOWED_ORIGINS`

### 2. **База данных**
- ✅ Все таблицы создаются автоматически через SQLAlchemy
- ✅ Миграции выполняются при первом запуске сервисов
- ✅ Каждый сервис использует отдельную базу данных

### 3. **Мониторинг**
- ✅ Health checks настроены для всех сервисов
- ✅ Логирование настроено в каждом сервисе
- ✅ PostgreSQL подключения используют connection pooling

## 📋 **ФАЙЛЫ ДЛЯ ТЕСТИРОВАНИЯ:**

### Локальное тестирование:
- `docker-compose.test.yml` - Конфигурация с локальным PostgreSQL
- `.env` - Локальные настройки для разработки

### Production развертывание:
- `docker-compose.yml` - Основная конфигурация для внешнего PostgreSQL
- `.env.example` - Шаблон настроек для production

## ✅ **ГОТОВНОСТЬ К РАЗВЕРТЫВАНИЮ:**

Все изменения выполнены и проект готов к развертыванию с внешним PostgreSQL сервером:

1. ✅ Techcard сервис переведен на PostgreSQL
2. ✅ Все сервисы настроены для работы с внешней БД
3. ✅ Созданы скрипты инициализации баз данных
4. ✅ Обновлены конфигурации Docker
5. ✅ Настроены переменные окружения
6. ✅ Добавлены health checks и мониторинг

**Следующий шаг**: Выполнить `init_auth_db.sql` на PostgreSQL сервере и запустить проект! 🚀