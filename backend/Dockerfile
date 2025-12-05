# backend/Dockerfile (полный файл)

# ========================================
# Этап 1: Сборка зависимостей
# ========================================
FROM python:3.11-slim AS builder

WORKDIR /app

# Минимум для сборки
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# ========================================
# Этап 2: Финальный образ
# ========================================
FROM python:3.11-slim AS production

WORKDIR /app

# libpq для psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Непривилегированный пользователь
RUN useradd --create-home appuser

# Ставим wheels
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*

# Копируем весь backend
COPY . .

# Создаём папку под SQLite с правами для appuser
RUN mkdir -p /app/data && chown -R appuser:appuser /app /app/data

USER appuser

EXPOSE 8000

# main.py в корне
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
