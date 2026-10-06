#!/usr/bin/env bash
# Локальный запуск CRM College без Docker.
#
# Поднимает три FastAPI-сервиса и фронтенд (Vite dev) в фоне/foreground.
# Использует SQLite (без DB_HOST) и общие dev-секреты.
#
# Использование:
#   ./scripts/dev_local.sh            # запустить всё
#   ./scripts/dev_local.sh --backend  # только backend-сервисы
#   ./scripts/dev_local.sh --frontend # только фронтенд
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="${PYTHON:-python3}"

# Общие dev-секреты (не для production).
export SECRET_KEY="${SECRET_KEY:-dev_secret_key_at_least_32_chars_long}"
export INTERNAL_API_TOKEN="${INTERNAL_API_TOKEN:-dev_internal_token}"
export ENVIRONMENT="${ENVIRONMENT:-development}"

AUTH_PORT=8002
SCHEDULE_PORT=8000
TECHCARD_PORT=8001

start_backend() {
  echo "▶ Запуск auth на :${AUTH_PORT}"
  (cd "$ROOT/backend/auth" && exec "$PYTHON" -m uvicorn main:app --host 127.0.0.1 --port "$AUTH_PORT") &
  echo "▶ Запуск schedule на :${SCHEDULE_PORT}"
  (cd "$ROOT/backend/schedule" && exec "$PYTHON" -m uvicorn main:app --host 127.0.0.1 --port "$SCHEDULE_PORT") &
  echo "▶ Запуск techcard на :${TECHCARD_PORT}"
  (cd "$ROOT/backend/techcard" && exec "$PYTHON" -m uvicorn main:app --host 127.0.0.1 --port "$TECHCARD_PORT") &
}

start_frontend() {
  echo "▶ Запуск фронтенда (Vite) на :3000"
  (cd "$ROOT/frontend" && exec npm run dev) &
}

case "${1:-}" in
  --backend)
    start_backend
    wait
    ;;
  --frontend)
    start_frontend
    wait
    ;;
  *)
    start_backend
    start_frontend
    wait
    ;;
esac
