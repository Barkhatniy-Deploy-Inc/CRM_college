# CRM College

Vue frontend, FastAPI services (auth, schedule, techcard), PostgreSQL и Nginx.

## Локальный запуск

Требуются запущенный Docker Desktop / Docker Engine с Compose v2+ и Python 3.

```bash
./scripts/local.sh init
./scripts/local.sh up
./scripts/local.sh check
```

Приложение: **http://localhost:8080**. `init` создаёт `.env` со случайными секретами; существующие настройки сохраняются, отсутствующий `INTERNAL_API_TOKEN` добавляется. Данные PostgreSQL хранятся в Docker volume. `make init`, `make up` и `make smoke` вызывают те же команды.

Для новой базы примените миграции до запуска приложения: `./scripts/local.sh migrate`. Старые файлы SQLite не переносятся автоматически: сначала сохраните их копии и согласуйте перенос с Глебом. Существующий PostgreSQL volume не удаляйте; перед изменением схемы проверьте резервную копию и процедуру восстановления.

## Ngrok

Добавьте `NGROK_AUTHTOKEN` в локальный `.env`, затем:

```bash
./scripts/local.sh tunnel
./scripts/local.sh url
```

Ngrok публикует Nginx: frontend, API и WebSocket доступны на одном HTTPS-домене. Инспектор: http://localhost:4040. Используйте демонстрационные данные до устранения оставшихся проблем регистрации, прав и WebSocket из плана.

Полная [инструкция запуска](docs/LOCAL_DEVELOPMENT.md), [PostgreSQL и резервное восстановление](docs/POSTGRESQL_LOCAL_RUNBOOK.md), [передача задач команде](docs/DEVOPS_HANDOFF.md).
