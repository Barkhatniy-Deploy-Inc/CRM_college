# backend/techcard/Dockerfile

# ========================================
# Этап 1: Сборка зависимостей
# ========================================
FROM python:3.11-slim AS builder

WORKDIR /app

# Установка зависимостей для сборки
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements и собираем wheels
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# ========================================
# Этап 2: Финальный образ
# ========================================
FROM python:3.11-slim AS production

WORKDIR /app

# Установка runtime зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Создание непривилегированного пользователя
RUN useradd --create-home --shell /bin/bash appuser

# Установка Python зависимостей
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/* && rm -rf /wheels

# Копирование исходного кода
COPY . .

# Создание необходимых директорий
RUN mkdir -p /app/data /app/logs /app/generated_docs && \
    chown -R appuser:appuser /app

# Переключение на непривилегированного пользователя
USER appuser

# Проверка здоровья
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

EXPOSE 8000

# Запуск приложения
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
