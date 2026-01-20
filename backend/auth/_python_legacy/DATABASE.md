# 🔄 Переключение между SQLite и PostgreSQL

## Текущая конфигурация

**По умолчанию используется SQLite** для локальной разработки. Это не требует настройки и работает "из коробки".

## SQLite (локально, по умолчанию)

Ничего настраивать не нужно! Просто запустите:

```bash
python main.py
```

Файл БД будет создан автоматически в `database/auth.db`

Если хотите явно указать:
```env
DB_TYPE=sqlite
SQLITE_PATH=database/auth.db
```

## PostgreSQL (production)

Для переключения на PostgreSQL:

1. Установите переменные окружения в `.env`:

```env
DB_TYPE=postgresql
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=auth_db
```

2. Убедитесь, что PostgreSQL запущен и база данных `auth_db` создана:

```sql
CREATE DATABASE auth_db;
```

3. Перезапустите приложение - оно автоматически подключится к PostgreSQL

## Миграция данных

При переключении с SQLite на PostgreSQL:

1. Экспортируйте данные из SQLite (если нужно)
2. Создайте структуру БД в PostgreSQL (автоматически при первом запуске)
3. Импортируйте данные (если нужно)

## Проверка текущей БД

При запуске приложения вы увидите:
```
✅ База данных инициализирована (SQLITE)
   SQLite файл: /path/to/database/auth.db
```

или

```
✅ База данных инициализирована (POSTGRESQL)
```

## Важно

- SQLite файл (`database/auth.db`) уже добавлен в `.gitignore`
- При переключении на PostgreSQL убедитесь, что драйвер `psycopg` установлен (уже в requirements.txt)
- Все модели работают одинаково с обеими БД благодаря SQLAlchemy

