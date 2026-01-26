.PHONY: setup build-local up all

setup:
	@echo "🔍 Setting up Prisma engines..."
	@PRISMA_ENGINE=$$(find ~/.cache/prisma/binaries -name "prisma-query-engine*" -type f | head -n 1); \
	if [ -z "$$PRISMA_ENGINE" ]; then \
		echo "❌ Prisma Query Engine not found in ~/.cache/prisma/binaries"; \
		exit 1; \
	fi; \
	echo "✅ Found engine: $$PRISMA_ENGINE"; \
	cp "$$PRISMA_ENGINE" backend/auth/prisma-query-engine; \
	cp "$$PRISMA_ENGINE" backend/schedule/prisma-query-engine; \
	cp "$$PRISMA_ENGINE" backend/techcard/prisma-query-engine; \
	chmod +x backend/auth/prisma-query-engine; \
	chmod +x backend/schedule/prisma-query-engine; \
	chmod +x backend/techcard/prisma-query-engine; \
	echo "✅ Prisma engines copied and made executable"

build-local:
	@echo "🔨 Building services locally..."
	@cd backend/common && go mod tidy
	@cd backend/auth && go mod edit -replace common=../common && go mod tidy && CGO_ENABLED=0 go build -o main .
	@cd backend/schedule && go mod edit -replace common=../common && go mod tidy && CGO_ENABLED=0 go build -o main .
	@cd backend/techcard && go mod edit -replace common=../common && go mod tidy && CGO_ENABLED=0 go build -o main .
	@echo "✅ Build complete"

up:
	@echo "🚀 Starting Docker Compose..."
	@docker compose up --build -d
	@echo "✅ Services started!"
	@docker compose ps

all: setup build-local up
