-- init.sql
-- Инициализация баз данных для микросервисов

-- Создание базы данных для auth сервиса
CREATE DATABASE auth_db;

-- Создание базы данных для schedule сервиса (если не существует)
-- Основная БД уже создается через POSTGRES_DB в docker-compose.yml

-- Создание пользователей и прав доступа
-- Пользователь для auth сервиса
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'auth_user') THEN

      CREATE ROLE auth_user LOGIN PASSWORD 'auth_password';
   END IF;
END
$do$;

-- Предоставляем права на auth_db
GRANT ALL PRIVILEGES ON DATABASE auth_db TO auth_user;

-- Подключаемся к auth_db для создания схемы
\c auth_db;

-- Создаем схему для auth сервиса
CREATE SCHEMA IF NOT EXISTS auth;

-- Предоставляем права на схему
GRANT ALL ON SCHEMA auth TO auth_user;
GRANT ALL ON ALL TABLES IN SCHEMA auth TO auth_user;
GRANT ALL ON ALL SEQUENCES IN SCHEMA auth TO auth_user;

-- Возвращаемся к основной БД
\c schedule_db;

-- Создаем схемы для schedule сервиса
CREATE SCHEMA IF NOT EXISTS schedule;
CREATE SCHEMA IF NOT EXISTS public;

-- Предоставляем права
GRANT ALL ON SCHEMA schedule TO postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON ALL TABLES IN SCHEMA schedule TO postgres;
GRANT ALL ON ALL SEQUENCES IN SCHEMA schedule TO postgres;
GRANT ALL ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO postgres;

-- Создаем расширения если нужны
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Логирование
SELECT 'Database initialization completed successfully' AS status;