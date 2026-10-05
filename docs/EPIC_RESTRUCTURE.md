# CRM-RESTRUCTURE — Стабилизация и реструктуризация CRM College до рабочего MVP

> **Примечание об адаптации.** Исходный workflow предполагает Jira и Confluence. В этом окружении они недоступны, поэтому эпик и тикеты выведены из самого репозитория, а «публикация» выполнена как файл в репозитории. Epic Key `CRM-RESTRUCTURE` — синтетический идентификатор для трассировки.

- **Epic Key:** CRM-RESTRUCTURE
- **Epic Title:** Стабилизация и реструктуризация CRM College до рабочего MVP
- **Jira Project:** нет доступа (repo-derived)
- **Publish Location:** `docs/EPIC_RESTRUCTURE.md`
- **Статус:** In Progress

---

## 1. Epic Overview

**Purpose.** Привести проект из состояния «частично собранная инфраструктура с конфликтующими контрактами» в состояние рабочего MVP: единая аутентификация, единая СУБД, согласованные API-контракты, функциональные техкарты.

**User Value.** Студент/преподаватель видит своё расписание; администратор управляет пользователями, группами, аудиториями, расписанием и техкартами без 404, без потери данных и без дублирования учётных записей.

**Scope (included).**
- Единый источник пользователей/ролей и единая проверка JWT.
- PostgreSQL как единственная runtime-СУБД, включая techcard.
- Согласование nginx ↔ FastAPI ↔ frontend контрактов.
- Функциональные techcards (list/create/update/download).
- Устранение неаутентифицированных и опасных endpoint'ов.
- Тесты, CI и миграции как основа дальнейшей разработки.

**Scope (excluded).**
- Визуальный конструктор расписания (drag & drop) — отдельный эпик после MVP.
- Редактор связей как UI (API уже частично есть).
- Уведомления/Telegram/календарь как продуктовая фича (только изоляция от импорта тестов).
- Микросервисное дробление, Kubernetes, мультитенантность.

**Key Stakeholders.** Администрация колледжа (владелец данных), преподаватели, студенты, команда разработки/сопровождения.

---

## 2. Epic Goals & Success Metrics

**Primary Goal.** Сквозные сценарии MVP работают через единый API, CI зелёный, данные не теряются при перезапуске.

**Success Metrics.**
- `docker compose up --build` поднимает стек; все health endpoints отвечают 200.
- Вход → управление пользователями → группы/аудитории → расписание → техкарта → скачивание DOCX проходят без ручных обходов.
- Ни один endpoint не принимает анонимную запись.
- `pytest` в трёх сервисах проходит и становится блокирующим в CI.
- Frontend `lint`, `format:check`, `test`, `build` — зелёные.

**KPIs.**
- 0 дублирующих таблиц пользователей.
- 0 endpoint'ов вне `/api` префикса, доступных через шлюз.
- 0 неаутентифицированных мутаций.
- 0 SQLite в runtime.

---

## 3. Requirements Summary

### Functional Requirements (EARS)

- **FR-1.** Когда пользователь отправляет корректные учётные данные, система должна выдать access+refresh токены и установить httpOnly cookies.
- **FR-2.** Когда сервис schedule/techcard получает запрос, система должна проверить токен, выпущенный **только** auth-сервисом, с проверкой `type == "access"`.
- **FR-3.** Когда администратор создаёт пользователя, система должна создать его без перезаписи сессии администратора.
- **FR-4.** Когда администратор запрашивает список техкарт, система должна вернуть постраничный список.
- **FR-5.** Когда пользователь создаёт техкарту, система должна присвоить серверный ID и владельца.
- **FR-6.** Когда пользователь скачивает техкарту, система должна сгенерировать DOCX по официальному шаблону.
- **FR-7.** Когда создаётся занятие, система должна запретить конфликт аудитории/преподавателя/группы (409).
- **FR-8.** Когда вызывается внутренний endpoint аудита, система должна требовать внутренний токен.
- **FR-9.** Когда приложение стартует в production, система должна использовать схему БД из миграций Alembic.
- **FR-10.** Когда фронтенд получает 401, система должна попытаться обновить токен и иначе разлогинить пользователя.

### Non-Functional Requirements

- **NFR-1. Security.** Пароли — только через body; токены — httpOnly cookies; `SECRET_KEY` обязателен и общий для сервисов; CORS ограничен доменами.
- **NFR-2. Reliability.** PostgreSQL как единственное хранилище; перезапуск контейнера не теряет данные.
- **NFR-3. Maintainability.** Один источник схем, разделение ORM/схем/сервисов; ruff+mypy в CI.
- **NFR-4. Testability.** >80% branch coverage на auth/schedule; in-memory SQLite для unit-тестов.
- **NFR-5. Performance.** Список расписания за неделю — < 1 c при типовом объёме.

### Business Rules

- Роли: `student`, `teacher`, `moderator`, `admin`. Мутации справочников — `moderator`/`admin`; пользователи/роли/аудит — `admin`.
- Идентичность определяется только auth-сервисом.
- Техкарта принадлежит автору; администратор видит все.

### Edge Cases

- Дубликат email при регистрации → 409/400 с понятным сообщением.
- Истёкший access → refresh → при неудаче logout.
- Импорт XLSX с некорректными строками → отчёт об ошибках, без частичной порчи данных.
- Пустой/битый `localStorage.user` → приложение не падает.
- Конкурентное создание занятия на тот же слот → 409.

---

## 4. Technical Change Overview

Оценка риска по 7-мерной шкале (Scope, Dependencies, Blocking, Stability, UX, Testing, Reversibility).

| Компонент | Тип | Описание | Risk | Зависимости |
|---|---|---|---|---|
| `backend/schedule/services/auth.py`, `routers/auth.py`, `database/models.py::User` | Refactor | Удалить legacy-auth; доверять токенам auth-сервиса | **High (17)** | Единый JWT-контракт |
| `backend/techcard/database/dependencies.py` | Refactor | PostgreSQL вместо SQLite | **High (16)** | Alembic, общий config |
| Alembic (новый) | New | Миграции вместо `create_all` | **Med (14)** | Единая схема |
| `nginx/nginx.conf` | Fix | Убрать мёртвые правила, согласовать префиксы | Low (9) | — |
| `backend/schedule/routers/{participants,export,notifications,calendar}.py` | Fix | Префиксы `/api/schedule/...` | Low (10) | nginx |
| `backend/techcard/routers/techcard_router.py` | Enhancement | list/create/update/download + auth | Med (13) | auth dependency |
| `backend/auth/routers/users.py` | Fix | Убрать дубль route, защитить internal audit | Med (11) | internal token |
| `backend/auth/routers/auth.py` | Fix | logout/refresh cookies | Low (8) | — |
| `frontend/src/store/*`, `core/utils/api.js` | Enhancement | Единый API-слой, 401/refresh, убрать localStorage-токен | Med (14) | Auth cookies |
| `frontend/src/features/**`, dead files | Refactor | Удаление мёртвого кода, унификация UI-ошибок | Low (10) | — |
| `docs/*`, `scripts/*`, `AGENTS.md` | Fix | Актуализация под единый API | Low (7) | Контракт |

**Risk profile:** Low — 6, Medium — 4, High — 2.

---

## 5. Impact Analysis

**Codebase Impact.**
- Backend: auth (routers/users/services), schedule (routers/services/database/dependencies), techcard (routers/database/utils).
- Frontend: `store/*`, `core/utils/api.js`, `features/*`, router.
- Инфраструктура: `nginx/nginx.conf`, `docker-compose.yml`, `db-init/init.sql`, `.env.example`.

**Data Model Changes.**
- Единая таблица `users` (auth) + `teacher`-профиль.
- `tech_cards.owner_id` + FK на auth user (или локальная копия по `user_id`).
- Уникальные ограничения: `groups.name`, `auditoriums.name`, `subjects.name`, link-таблицы.
- Индексы на `class_slots(group_id, start_time)`, `(teacher_id, start_time)`, `(auditorium_id, start_time)`.
- Миграции Alembic: baseline → перенос данных.

**API Changes.**
- Все домены под `/api/v1` (или сохранение текущих префиксов на переходный период).
- techcard: `GET/POST /api/techcards`, `GET/PUT/DELETE /api/techcards/{id}`, `GET /api/techcards/{id}/download`.
- schedule sub-routers: `/api/schedule/{participants,export,notifications,calendar}`.
- Удаление legacy `/api/auth/*` из schedule.

**UI/UX Changes.**
- Удаление неработающих кнопок; корректные пути; toast вместо `alert`.
- Восстановление сессии через `/auth/me` и refresh.

**Migration Strategy.**
1. Ввести единый config и Alembic baseline.
2. Создать `techcard_db` схему; перенести данные из SQLite (если есть).
3. Переключить сервисы на общий JWT-контракт.
4. Обновить nginx и фронтенд одновременно с бэкендом.

**Rollback Plan.**
- Инфраструктурные изменения — через `git revert` (нет миграций данных на первом шаге).
- Миграции Alembic — `alembic downgrade -1`; перед продакшеном — дамп БД.
- Nginx/Compose — отдельные коммиты для быстрого отката.

**Tradeoffs.**
- Полный модульный монолит отложен: сначала выравнивание контрактов (меньше риск).
- Сохранение префиксов `/api/...` на переходный период вместо немедленного `/api/v1`.
- Backend-тесты временно не блокируют CI до их выравнивания.

---

## 6. Testing Strategy

- **Unit:** сервисы auth (token, security, audit, session), schedule (slots conflict, importer), techcard (docx generator). Цель — 80% branch.
- **Integration/API:** httpx + ASGITransport, in-memory SQLite через `dependency_overrides` (шаблон `backend/auth/tests/conftest.py:12-49`).
- **API-контракты:** отдельный тест-набор на пути, используемые фронтендом (защита от рассинхрона nginx ↔ backend ↔ frontend).
- **Test Data:** фабрики пользователей/групп/аудиторий/слотов; фикстуры XLSX из `backend/schedule/РАСПИСАНИЕ/`; тестовый DOCX-шаблон.
- **Coverage Goals:** auth ≥ 85%, schedule ≥ 80%, techcard ≥ 75% (после переноса в PG).
- **Изоляция:** тесты не должны писать в реальные БД (исправить `backend/techcard/tests/conftest.py`, убрать реальный SMTP из `test_email.py`).

---

## 7. User Behavior Testing

**E2E Scenarios (Playwright, `frontend/e2e/`).**
1. Вход администратора → редирект на `/dashboard`.
2. Создание пользователя → он появляется в списке; сессия администратора не сбрасывается.
3. Создание группы и аудитории → доступны в селектах расписания.
4. Создание занятия → отображается в сетке недели; конфликт аудитории → понятная ошибка.
5. Создание техкарты → сохранение → скачивание DOCX.
6. Истёкший access → автоматический refresh без разлогина.

**Acceptance Test Cases.**
- Given администратор вошёл, When создаёт пользователя, Then admin-сессия сохраняется и пользователь виден в списке.
- Given два занятия в одной аудитории, When создаётся второе, Then 409 и сообщение.
- Given истёкший access-токен, When выполняется запрос, Then токен обновляется и запрос повторяется.

**Regression.**
- Вход/выход, список пользователей, аудит-логи, группы, аудитории, расписание недели.

---

## 8. Implementation Notes

**Patterns to Follow.**
- Router → service (`api/*_api.py`) → session: `backend/schedule/routers/groups.py:15-40` + `api/groups_api.py`.
- Pydantic Base/Create/Update/Response: `backend/auth/database/schemas.py:9-105`.
- Auth guards: `backend/auth/dependencies.py:90-123`.
- Test fixtures: `backend/auth/tests/conftest.py:12-49`.
- Frontend store + API client: `frontend/src/store/admin.js`, `frontend/src/core/utils/api.js`.

**Architecture Decisions.**
- Auth — единственный источник идентичности; остальные сервисы валидируют его JWT.
- PostgreSQL — единственная runtime-БД; SQLite только в тестах.
- Alembic — единственный способ менять схему.
- Внутренние вызовы — с internal-токеном.

**Technical Debt.**
- `create_all` до внедрения Alembic.
- Дубли схем ORM/Pydantic в schedule до разделения.
- `alert()`/`console.log` до появления toast-слоя.

**Security Considerations.**
- Убрать `SECRET_KEY`-fallback; обязательный общий ключ.
- Убрать токен из `localStorage`; httpOnly cookies + CSRF.
- Закрыть `audit-log/internal`, relations, techcard, export.
- Ограничить CORS; `secure` cookies в prod; refresh-rotation.

---

## 9. Acceptance Criteria

- [ ] FR-1…FR-10 реализованы и покрыты тестами.
- [ ] Нет дублирующих таблиц пользователей; единый JWT-контракт.
- [ ] techcard работает на PostgreSQL и имеет list/create/update/download.
- [ ] Все endpoint'ы достижимы через шлюз; нет мёртвых правил nginx.
- [ ] Нет неаутентифицированных мутаций и внутренних endpoint'ов.
- [ ] `pytest` (3 сервиса) и frontend `lint/format:check/test/build` — зелёные.
- [ ] E2E-сценарии 1–6 проходят.
- [ ] Документация (`AGENTS.md`, `docs/*`, `scripts/*`) соответствует API.
- [ ] Security review пройден; gitleaks и pip-audit зелёные.

---

## 10. Open Questions & Risks

**Blockers.**
- Нет доступа к Jira/Confluence — трассировка ведётся в этом файле.
- Локально доступен только Python 3.14; сервисы таргетят 3.11 → backend-тесты нельзя прогнать локально без 3.11.
- Нужны реальные данные SQLite `techcards.db` для решения о миграции.

**Unknowns.**
- Есть ли реальные пользовательские данные в `auth_db`/`schedule_db` на целевой среде.
- Требуется ли `/api/v1` немедленно или допустим переходный период.
- Нужны ли participants/notifications/calendar как продуктовая фича.

**Assumptions.**
- Один инстанс каждого сервиса (нет горизонтального масштабирования).
- Часовой пояс колледжа фиксирован; БД хранит UTC.

**Risks & Mitigation.**
- **R1. Потеря данных при переносе techcard SQLite→PG.** → Бэкап, миграционный скрипт с проверкой количества записей, dry-run.
- **R2. Поломка расписания при смене auth.** → Переходный период с двойной валидацией, контрактные тесты.
- **R3. Большой diff форматирования/рефакторинга.** → Отдельные коммиты по слоям; форматирование уже вынесено отдельно.
- **R4. Слабый `SECRET_KEY` в compose.** → Обязательный `.env`, fail-fast в prod.

---

## 11. Codebase Analysis

**Affected Modules.**
- `backend/auth/` — routers `auth|users` (+ не подключён `sessions`), services `security|token|session|audit|user|cookie|search`, middleware `rate_limit`, `database/{models,schemas,database}`.
- `backend/schedule/` — `main.py`, routers `schedule|groups|auditoriums|participants|export|notifications|calendar|relations|auth(legacy)`, services `auth|schedule_importer|schedule_exporter|audit_logger|notifications|websocket_manager`, `database/{models,database}`, `api/*`.
- `backend/techcard/` — `main.py`, `routers/techcard_router.py` (+ пустой `dictionaries_router.py`), `database/{dependencies,models_techcard,schemas}`, `utils/docx_generator.py`, `templates/`.
- `frontend/src/` — `store/*`, `core/utils/api.js`, `router/index.js`, `features/{auth,dashboard,schedule,admin,techcards}/views`, `core/{components,layouts,styles}`.
- Инфра: `nginx/nginx.conf`, `docker-compose.yml`, `db-init/init.sql`, `.env.example`, `scripts/*`, `docs/*`.

**Patterns Discovered.**
- API: разные префиксы; часть router'ов без `/api`; auth через cookie+Bearer с разными контрактами.
- Тесты: pytest-asyncio (`asyncio_mode=auto`), in-memory SQLite + `dependency_overrides`; `mock_auth` подменяет не ту зависимость.
- Frontend: Options API Pinia, `<script setup>`, `Base*` компоненты, `isLoading`/`error` флаги, ошибки в `console`/`alert`.
- DB: `create_all`, `echo=True` в prod, techcard на SQLite.

**Reference Implementations.**
- CRUD + сервис: `backend/schedule/routers/groups.py` + `api/groups_api.py`.
- Auth: `backend/auth/services/{token_service,security,session_service,audit_service}.py`, `routers/sessions.py`.
- Тесты: `backend/auth/tests/conftest.py`, `backend/schedule/tests/conftest.py`.
- Frontend: `frontend/src/store/admin.js`, `frontend/src/features/admin/views/UsersManagementView.vue`.

**Test Locations & Conventions.**
- Backend: `backend/<service>/tests/`, файлы `test_*.py`, фикстуры `conftest.py`.
- Frontend unit: `frontend/src/**/__tests__/*.spec.js` (Vitest).
- E2E: `frontend/e2e/*.spec.js` (Playwright, исключён из Vitest).

---

## 12. Linked Tickets

**Epic:** CRM-RESTRUCTURE — Стабилизация и реструктуризация CRM College до рабочего MVP

Тикеты выведены из репозитория (Jira недоступна).

| Key | Summary | Type | Risk | Фаза |
|---|---|---|---|---|
| CRM-1 | Удалить мёртвый код и пустые модули | Task | Low | 0 |
| CRM-2 | Исправить logout/refresh cookies в auth | Bug | Low | 0 |
| CRM-3 | Убрать дубль `GET /api/users/{id}` | Bug | Low | 0 |
| CRM-4 | Защитить `audit-log/internal` внутренним токеном | Security | Med | 0 |
| CRM-5 | Устранить `is_active` AttributeError в schedule | Bug | Low | 0 |
| CRM-6 | Согласовать nginx и префиксы schedule-роутеров | Fix | Low | 1 |
| CRM-7 | Techcard: list/create/update/download + auth | Feature | Med | 1 |
| CRM-8 | Techcard: PostgreSQL вместо SQLite | Refactor | High | 2 |
| CRM-9 | Alembic: baseline и миграции | Infra | Med | 2 |
| CRM-10 | Единый JWT-контракт, удалить legacy-auth schedule | Refactor | High | 2 |
| CRM-11 | Frontend: единый API-слой, 401/refresh, убрать localStorage | Feature | Med | 3 |
| CRM-12 | Тесты: выровнять и сделать блокирующими | Quality | Med | 3 |
| CRM-13 | Документация и скрипты под единый API | Docs | Low | 3 |
| CRM-14 | E2E-сценарии 1–6 | Quality | Med | 4 |

---

## Implementation TODO Checklist

### Фаза 0 — Безопасность и мёртвый код (выполнено)
- [x] CRM-1 Удалить мёртвые файлы
- [x] CRM-2 Исправить logout/refresh cookies
- [x] CRM-3 Убрать дубль `GET /api/users/{id}`
- [x] CRM-4 Защитить `audit-log/internal`
- [x] CRM-5 Устранить `is_active` AttributeError
- [x] Techcard: исправить путь к DOCX-шаблону
- [x] Исправить `mock_auth` в schedule-тестах (патчил не ту зависимость)

### Фаза 1 — Контракты (выполнено)
- [x] CRM-6 nginx + префиксы schedule
- [x] CRM-7 Techcard list/create/update/download + auth
- [x] Frontend store techcard под реальные пути (+ create, `/techcards/new`)
- [x] Обновлены `requirements.txt` techcard (`PyJWT`), `.env.example`, `docker-compose.yml`, `AGENTS.md`

### Фаза 2 — Данные и идентичность
- [x] CRM-8 Techcard → PostgreSQL (конфигурируемый движок)
- [x] CRM-9 Alembic baseline (upgrade/downgrade проверены на SQLite)
- [~] CRM-10 Единый JWT: токены выпускает только auth; schedule валидирует access-JWT и роли. Консолидация модели `User` — отдельный шаг.

### Фаза 3 — Frontend и тесты
- [x] CRM-11 API-слой + refresh + bootstrap `/auth/me`
- [x] CRM-12 Тесты выровнены; backend-CI с покрытием 75/50/60 и без `continue-on-error`
- [ ] CRM-13 Документация

### Фаза 4 — E2E
- [ ] CRM-14 Playwright-сценарии

---

## Risk Assessment Detail (для High-риск изменений)

**CRM-10 (единый JWT, удаление legacy-auth).** Scope 3, Dependencies 3, Blocking 3, Stability 2, UX 3, Testing 3, Reversibility 2 → **19 (High)**. Требуется spike/контрактный тест до внедрения; поставка по шагам: сначала dual-validate, затем удаление.

**CRM-8 (techcard → PostgreSQL).** Scope 2, Dependencies 3, Blocking 2, Stability 2, UX 2, Testing 3, Reversibility 2 → **16 (High/Med граница)**. Нужен бэкап и миграционный скрипт с проверкой.
