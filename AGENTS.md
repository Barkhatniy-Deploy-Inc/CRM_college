# Инструкции для OpenCode

## Структура проекта

- Это приложение из четырёх сервисов: Vue-фронтенд и три FastAPI-сервиса.
- Основной запуск выполняется через `docker-compose.yml`: Nginx, PostgreSQL, `auth`, `schedule`, `techcard` и `frontend`.
- Точки входа бэкенда:
  - `backend/auth/main.py`
  - `backend/schedule/main.py`
  - `backend/techcard/main.py`
- Точка входа фронтенда — `frontend/src/main.js`.
- Во фронтенде:
  - `frontend/src/features/` — функциональные модули;
  - `frontend/src/core/` — общие компоненты, layouts, views и утилиты;
  - `frontend/src/store/` — Pinia-хранилища;
  - `frontend/src/router/` — маршрутизация и проверки авторизации.

## Запуск

- Для запуска всего стека из корня используйте:
  ```bash
  docker compose up --build
  ```
- Внешние порты:
  - `3000` — фронтенд;
  - `8000` — schedule;
  - `8001` — techcard;
  - `8002` — auth;
  - `80` — Nginx-шлюз.
- Внутри Docker-сети сервисы слушают порт `8000`; для межсервисных запросов используйте имена сервисов (`auth`, `schedule`, `techcard`), а не внешние порты.
- Переменные окружения берите из `.env.example`. Секреты и рабочие `.env` не добавляйте в Git.

## Фронтенд

Рабочий каталог фронтенда — `frontend/`.

```bash
npm ci
npm run dev
npm run build
npm run test
```

- Тесты запускаются Vitest в окружении `jsdom`.
- Один тест или файл можно запустить так:
  ```bash
  npx vitest run src/store/__tests__/auth.spec.js
  ```
- В режиме разработки Vite слушает порт `3000` и проксирует `/api` на `http://localhost:80`.
- Axios по умолчанию использует `/api`; изменение API-маршрутов требует проверки Vite-конфига и корневого `nginx/nginx.conf`.

## Бэкенд

- У каждого сервиса свои `requirements.txt`, `pytest.ini` и каталог `tests/`.
- Python-зависимости устанавливайте из каталога конкретного сервиса:
  ```bash
  cd backend/auth
  pip install -r requirements.txt
  ```
  Аналогично для `backend/schedule` и `backend/techcard`.
- Каждый сервис запускается из собственного каталога:
  ```bash
  python main.py
  ```
- Запуск тестов выполняйте из каталога соответствующего сервиса:
  ```bash
  pytest
  ```
- Фокусированный запуск:
  ```bash
  pytest tests/test_relations_api.py -q
  ```
- Для тестов `techcard` установите `TESTING=1`, чтобы код выбрал in-memory SQLite:
  ```bash
  TESTING=1 pytest
  ```
- Тесты `auth` и `schedule` используют in-memory SQLite через фикстуры и переопределение зависимостей базы данных.
- В `schedule/tests/` есть тесты интеграций с email и Telegram. Они могут требовать переменные окружения или внешние настройки; для обычной проверки запускайте конкретные API/model-тесты.

## API-маршрутизация

Публичная маршрутизация задаётся в `nginx/nginx.conf`:

- `/api/auth` и `/api/users` → `auth`;
- `/api/schedule` (включая `groups`, `auditoriums`, `export`, `participants`, `calendar`, `notifications`) → `schedule`;
- `/api/relations` → `schedule`;
- `/api/techcards` и `/api/techcard` → `techcard`;
- остальные запросы → `frontend`.

При добавлении или изменении endpoint проверяйте одновременно:

1. router соответствующего FastAPI-сервиса;
2. URL, используемый фронтендом;
3. правило маршрутизации в `nginx/nginx.conf`;
4. тест соответствующего сервиса.

## База данных

- PostgreSQL создаёт три базы из `db-init/init.sql`:
  - `auth_db`;
  - `schedule_db`;
  - `techcard_db`.
- `db-init/init.sql` выполняется только при первоначальном создании PostgreSQL volume. Изменение этого файла не применяет изменения к уже существующему volume.
- Схема БД управляется Alembic: у каждого сервиса свой `alembic/` и baseline-миграция. Применяйте изменения через:
  ```bash
  make migrate    # alembic upgrade head во всех сервисах
  cd backend/auth && alembic revision --autogenerate -m "message"
  ```
- `create_all` в `lifespan` пока остаётся как временный fallback и будет удалён после полного перехода на миграции.
- Не удаляйте PostgreSQL volume без явного намерения потерять локальные данные.

## Инструменты качества

- В корне есть `Makefile` с едиными командами: `make help`, `make up`, `make test`, `make lint`, `make format`, `make typecheck`, `make security`, `make smoke`.
- Backend-инструменты описаны в корневом `pyproject.toml` и `requirements-dev.txt`. Устанавливайте их вместе с зависимостями сервиса:
  ```bash
  cd backend/auth
  pip install -r requirements.txt -r ../../requirements-dev.txt
  ruff check .
  ```
- `ruff` настроен как блокирующий линтер. Конфигурация общая для всех сервисов и находится в корневом `pyproject.toml`; запускайте `ruff check .` из каталога сервиса.
- `mypy` и `bandit` подключены как вспомогательные и пока не блокируют CI.
- Frontend: `npm run lint` (ESLint, конфиг `frontend/eslint.config.js`), `npm run format` / `npm run format:check` (Prettier), `npm run test:e2e` (Playwright, требует запущенного стека).
- CI прогоняет `npm run lint`, `npm run format:check`, `npm run test`, `npm run build`. Перед коммитом форматируйте через `npm run format`.
- E2E-тесты Playwright лежат в `frontend/e2e/` и исключены из Vitest через `vite.config.js`. Перед первым запуском нужен `npx playwright install`.
- `pre-commit` конфиг — `.pre-commit-config.yaml`: установка `pip install pre-commit && pre-commit install`.
- CI — `.github/workflows/ci.yml`. Backend-тесты запускаются с покрытием и порогом `--cov-fail-under` (auth 75, schedule 50, techcard 60) и блокируют CI. Ruff и frontend-проверки блокирующие.

## Проверка изменений

Для изменений во фронтенде:

```bash
cd frontend
npm run lint
npm run test
npm run build
```

Для изменений в одном бэкенд-сервисе:

```bash
cd backend/<service>
ruff check .
pytest
```

Перед проверкой межсервисных изменений запускайте стек через Docker Compose и проверяйте health endpoints:

```bash
curl http://localhost:8002/api/auth/health
curl http://localhost:8000/api/schedule/health
curl http://localhost:8001/api/techcard/health
```

Общие команды запускайте из корня через `make` (см. `make help`).
