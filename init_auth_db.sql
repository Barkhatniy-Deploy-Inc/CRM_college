-- init_auth_db.sql
-- Скрипт для инициализации базы данных auth_db в PostgreSQL

-- Создание базы данных auth_db (если не существует)
-- Этот скрипт должен быть выполнен администратором PostgreSQL

-- Подключение к PostgreSQL как суперпользователь
-- psql -U postgres -h your-postgres-server.com

-- Создание базы данных для auth сервиса
CREATE DATABASE auth_db
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.utf8'
    LC_CTYPE = 'en_US.utf8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

-- Создание базы данных для techcard сервиса
CREATE DATABASE techcard_db
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.utf8'
    LC_CTYPE = 'en_US.utf8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

-- Подключение к auth_db
\c auth_db;

-- Создание расширений для auth_db
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Создание схемы для auth сервиса (опционально)
CREATE SCHEMA IF NOT EXISTS auth;

-- Предоставление прав пользователю postgres
GRANT ALL PRIVILEGES ON DATABASE auth_db TO postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA auth TO postgres;

-- Подключение к techcard_db
\c techcard_db;

-- Создание расширений для techcard_db
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Создание схемы для techcard сервиса (опционально)
CREATE SCHEMA IF NOT EXISTS techcard;

-- Предоставление прав пользователю postgres
GRANT ALL PRIVILEGES ON DATABASE techcard_db TO postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA techcard TO postgres;

-- Создание таблиц будет выполнено автоматически через SQLAlchemy
-- при первом запуске auth сервиса

-- Логирование успешной инициализации
SELECT 'auth_db database initialized successfully' AS status;

-- Информация о созданной базе данных
SELECT 
    datname as database_name,
    pg_encoding_to_char(encoding) as encoding,
    datcollate as collate,
    datctype as ctype
FROM pg_database 
WHERE datname = 'auth_db';