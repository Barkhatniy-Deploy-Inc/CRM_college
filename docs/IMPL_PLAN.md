# CRM-RESTRUCTURE — Implementation Plan

**Overview Document:** [`docs/EPIC_RESTRUCTURE.md`](./EPIC_RESTRUCTURE.md)
**Epic Key:** CRM-RESTRUCTURE
**Статус:** In Progress (Фазы 0–1 завершены, Фаза 2 в работе)

Этот документ разбивает эпик на исполнимые тикеты: точные файлы, шаги, зависимости и команды проверки. Порядок обязателен там, где указана зависимость.

---

## Принципы исполнения

1. Каждый тикет — отдельный проверяемый шаг; не смешивать функциональные изменения с массовым форматированием.
2. Для backend-тикетов обязательны `ruff check .` и `python -m compileall`; для frontend — `npm run lint && npm run format:check && npm run test && npm run build`.
3. High-risk тикеты (CRM-8, CRM-10) выполняются с бэкапом данных и на запущенном стеке (Python 3.11), а не вслепую.
4. Тесты, которые «проходят» за счёт моков несуществующих путей, считаются дефектом и выравниваются вместе с контрактом.

---

## Граф зависимостей

```
CRM-1..CRM-7 (готово)
        │
        ├── CRM-8 (techcard → PostgreSQL) ──┐
        │                                   ├── CRM-9 (Alembic) ── CRM-10 (единый JWT)
        └── CRM-11 (frontend API) ──────────┘
                                             │
                                   CRM-12 (тесты/CI) ── CRM-13 (docs) ── CRM-14 (E2E)
```

- **CRM-9** зависит от CRM-8 (techcard должен уметь PostgreSQL до генерации миграций).
- **CRM-10** зависит от CRM-9 (схема фиксируется миграциями).
- **CRM-12** зависит от CRM-8 и CRM-10 (тесты выравниваются под итоговый контракт).
- **CRM-11** независим и может идти параллельно CRM-8.

---

## CRM-8 — Techcard: PostgreSQL вместо SQLite

**Цель.** techcard использует ту же СУБД, что и остальные сервисы; данные не теряются при пересборке контейнера.

**Зависимости.** нет.

**Файлы.**
- `backend/techcard/database/dependencies.py` — выбор движка.
- `docker-compose.yml` — env `TECHCARD_DB_NAME`, `DB_*` (уже есть).
- `backend/techcard/tests/conftest.py` — in-memory через `TESTING=1`.

**Шаги.**
1. Выбор движка по приоритету: `TESTING=1` → `sqlite:///:memory:` (+`StaticPool`); иначе `DB_HOST` → `postgresql+psycopg://...`; иначе локальный SQLite.
2. `echo` включать только при `DEBUG=true`.
3. Для PostgreSQL — `pool_pre_ping`, `pool_size`, `max_overflow`.
4. Не менять публичный интерфейс `get_techcard_db()`.

**Проверка.**
```bash
cd backend/techcard
ruff check .
python -m compileall .
TESTING=1 pytest -q   # на Python 3.11
```

**Риск.** Medium. Без `DB_HOST` поведение прежнее (SQLite), поэтому локальная разработка не ломается.

---

## CRM-9 — Alembic: baseline и миграции

**Цель.** Изменения схемы применяются миграциями, а не `create_all`.

**Зависимости.** CRM-8.

**Файлы.**
- `backend/<service>/alembic.ini`, `backend/<service>/alembic/env.py`, `backend/<service>/alembic/versions/0001_baseline.py`.

**Шаги.**
1. Для каждого сервиса инициализировать Alembic с `target_metadata = Base.metadata`.
2. Сгенерировать baseline на пустой БД; проверить `alembic upgrade head` и `downgrade -1`.
3. Добавить `make migrate` (`alembic upgrade head`) и шаг миграций перед стартом приложения в Compose.
4. Убрать `create_all` из `lifespan` после успешного внедрения.

**Проверка.**
```bash
alembic upgrade head && alembic downgrade -1 && alembic upgrade head
```

**Риск.** Medium. Требует запущенного PostgreSQL.

---

## CRM-10 — Единый JWT, удаление legacy-auth schedule

**Цель.** Идентичность определяется только auth-сервисом.

**Зависимости.** CRM-9.

**Файлы.**
- Удалить: `backend/schedule/routers/auth.py`, `backend/schedule/services/auth.py`, `User` из `backend/schedule/database/models.py`.
- `backend/schedule/dependencies.py` — валидировать токен auth (claims: `user_id`, `email`, `role`, `type="access"`).
- `backend/auth/main.py` — подключить `sessions.router`.
- `nginx/nginx.conf` — уже не маршрутизирует legacy.

**Шаги.**
1. Переходный период: schedule принимает токены auth и логирует расхождения.
2. Заменить schedule `dependencies.get_current_user` на общий валидатор (общий модуль или дублированная проверка с единым контрактом).
3. Удалить legacy-роутер и модель `User`.
4. Запретить анонимные мутации: relations, export, participants.
5. Добавить `require_role` для schedule-мутаций (moderator/admin).

**Проверка.**
- Токен auth проходит в schedule; токен schedule (legacy) больше не выпускается.
- `GET /api/relations/subjects` без токена → 401.

**Риск.** High. Нужен запущенный стек и контрактные тесты.

---

## CRM-11 — Frontend: API-слой, 401/refresh, bootstrap

**Цель.** Сессия не распадается при истечении access-токена; ошибки обрабатываются централизованно.

**Зависимости.** нет (совместимо с текущим backend).

**Файлы.**
- `frontend/src/core/utils/api.js` — интерцептор 401 + refresh + retry.
- `frontend/src/store/auth.js` — `fetchMe()`.
- `frontend/src/main.js` или `App.vue` — bootstrap сессии.

**Шаги.**
1. Response-интерцептор: на 401 (кроме `/auth/login`, `/auth/refresh`) один раз обновить токен через `POST /auth/refresh` и повторить запрос.
2. При неудаче refresh — очистить сессию и перейти на `/`.
3. Добавить `authStore.fetchMe()` → `GET /auth/me`.
4. Вызывать `fetchMe()` при старте, если есть признаки сессии.
5. Убрать отладочные `console.log` из API-клиента.

**Проверка.**
```bash
cd frontend
npm run lint && npm run format:check && npm run test && npm run build
```

**Риск.** Medium. Логин/refresh исключены из интерцептора, поэтому цикл исключён.

---

## CRM-12 — Тесты и блокирующий CI

**Зависимости.** CRM-8, CRM-10.

**Шаги.**
1. Выровнять тесты под единый API (убрать ожидания несуществующих путей).
2. Убрать `continue-on-error` у backend-тестов в `.github/workflows/ci.yml`.
3. Добавить покрытие: `pytest --cov` с порогом.
4. Добавить контрактные тесты: пути фронтенда ↔ роуты бэкенда.

**Проверка.** CI зелёный без `continue-on-error`.

---

## CRM-13 — Документация и скрипты

**Шаги.**
1. Обновить `AGENTS.md`, `docs/*`, `scripts/test_services.py`, `scripts/quick_test.sh` под единый API.
2. Удалить/переписать устаревшие `docs/PROJECT_ANALYSIS_REPORT.md` (React) и `docs/TESTING_GUIDE.md` (несуществующие compose-файлы).
3. Обновить Postman-коллекцию.

---

## CRM-14 — E2E (Playwright)

**Шаги.**
1. `frontend/e2e/auth.spec.js` — вход/выход, refresh.
2. `frontend/e2e/admin.spec.js` — создание пользователя без сброса своей сессии.
3. `frontend/e2e/schedule.spec.js` — создание занятия, конфликт 409.
4. `frontend/e2e/techcards.spec.js` — создание и скачивание DOCX.

**Проверка.** `npm run test:e2e` на запущенном стеке.

---

## Чек-лист исполнения

- [x] CRM-1 Мёртвый код
- [x] CRM-2 logout/refresh cookies
- [x] CRM-3 дубль `GET /api/users/{id}`
- [x] CRM-4 internal audit token
- [x] CRM-5 schedule `is_active`
- [x] CRM-6 nginx + префиксы
- [x] CRM-7 techcard CRUD + auth
- [x] CRM-8 techcard → PostgreSQL (конфигурируемый движок)
- [x] CRM-9 Alembic baseline (upgrade/downgrade проверены)
- [~] CRM-10 единый JWT: schedule больше не выпускает токены, валидирует auth-JWT, мутации под ролями. Осталось: консолидация `schedule.User`/teacher-профиля (рискованно, отдельно)
- [x] CRM-11 frontend API/refresh
- [x] CRM-12 тесты выровнены, CI-гейт честный (покрытие auth 75 / schedule 50 / techcard 60)
- [ ] CRM-13 документация
- [ ] CRM-14 E2E
