# Единые команды разработки CRM College.
# Помощь: make help

SHELL := /bin/bash
COMPOSE := docker compose

.PHONY: help up down build logs ps restart dev-local test test-frontend test-backend lint format typecheck security smoke migrate revision

help: ## Показать список команд
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

up: ## Поднять весь стек
	$(COMPOSE) up --build -d

down: ## Остановить стек
	$(COMPOSE) down

build: ## Пересобрать образы
	$(COMPOSE) build

logs: ## Показать логи
	$(COMPOSE) logs -f

ps: ## Статус контейнеров
	$(COMPOSE) ps

restart: down up ## Перезапустить стек

dev-local: ## Локальный запуск без Docker (SQLite + Vite dev)
	./scripts/dev_local.sh

test: test-frontend test-backend ## Все тесты

test-frontend: ## Тесты фронтенда
	cd frontend && npm run test

test-backend: ## Тесты backend-сервисов
	cd backend/common && pytest -q
	cd backend/auth && TESTING=1 pytest -q
	cd backend/schedule && TESTING=1 pytest -q
	cd backend/techcard && TESTING=1 pytest -q
lint: ## Линтеры backend и frontend
	ruff check backend
	(cd backend/common && ruff check .)
	cd frontend && npm run lint

format: ## Форматирование backend и frontend
	ruff format backend
	cd frontend && npm run format

typecheck: ## Проверка типов backend
	mypy backend

security: ## Сканирование секретов и уязвимостей
	gitleaks detect --config .gitleaks.toml --source . --redact --no-banner
	for req in backend/auth/requirements.txt backend/schedule/requirements.txt backend/techcard/requirements.txt; do \
		echo "== pip-audit $$req =="; pip-audit -r "$$req"; \
	done

smoke: ## Проверка health endpoints запущенного стека
	curl -fsS http://localhost:8002/api/auth/health
	curl -fsS http://localhost:8000/api/schedule/health
	curl -fsS http://localhost:8001/api/techcard/health

migrate: ## Применить миграции Alembic во всех сервисах
	cd backend/auth && alembic upgrade head
	cd backend/schedule && alembic upgrade head
	cd backend/techcard && alembic upgrade head

revision: ## Создать миграцию: make revision SERVICE=auth M="message"
	cd backend/$(SERVICE) && alembic revision --autogenerate -m "$(M)"
