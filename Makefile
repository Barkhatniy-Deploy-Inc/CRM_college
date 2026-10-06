# Единые команды разработки CRM College.
# Помощь: make help

SHELL := /bin/bash
COMPOSE := docker compose

.PHONY: help init up down build logs ps restart tunnel tunnel-url test test-frontend test-backend lint format typecheck security smoke migrate revision

help: ## Показать список команд
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

init: ## Создать .env со случайными секретами
	./scripts/local.sh init

up: ## Поднять весь стек и дождаться healthcheck
	./scripts/local.sh up

down: ## Остановить стек и ngrok, сохранить данные
	./scripts/local.sh down

build: ## Пересобрать образы
	$(COMPOSE) build

logs: ## Показать логи
	$(COMPOSE) logs -f

ps: ## Статус контейнеров
	$(COMPOSE) ps

restart: down up ## Перезапустить стек

tunnel: ## Запустить ngrok (нужен NGROK_AUTHTOKEN)
	./scripts/local.sh tunnel

tunnel-url: ## Показать HTTPS URL ngrok
	./scripts/local.sh url

test: test-frontend test-backend ## Все тесты

test-frontend: ## Тесты фронтенда
	cd frontend && npm run test

test-backend: ## Тесты backend-сервисов
	cd backend/auth && TESTING=1 pytest -q
	cd backend/schedule && TESTING=1 pytest -q
	cd backend/techcard && TESTING=1 pytest -q
lint: ## Линтеры backend и frontend
	ruff check backend
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

smoke: ## Проверка frontend и API через gateway (BASE_URL=...)
	./scripts/local.sh check $(if $(BASE_URL),"$(BASE_URL)",)

migrate: ## Применить миграции к PostgreSQL в Compose
	./scripts/local.sh migrate

revision: ## Создать миграцию: make revision SERVICE=auth M="message"
	cd backend/$(SERVICE) && alembic revision --autogenerate -m "$(M)"
