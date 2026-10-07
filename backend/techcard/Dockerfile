# Techcard Service Dockerfile
# ========================================
# Этап 1: Сборка зависимостей
# ========================================
FROM python:3.11-slim AS builder

WORKDIR /app

RUN sed -i \
    -e 's|http://deb.debian.org|https://deb.debian.org|g' \
    -e 's|http://security.debian.org|https://security.debian.org|g' \
    /etc/apt/sources.list.d/debian.sources 2>/dev/null || true
RUN apt-get -o Acquire::Retries=5 update && apt-get install -y --no-install-recommends \
    gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /app/wheels -r requirements.txt

# ========================================
# Этап 2: Финальный образ
# ========================================
FROM python:3.11-slim AS production

WORKDIR /app

# libpq для psycopg2, curl для healthcheck
RUN sed -i \
    -e 's|http://deb.debian.org|https://deb.debian.org|g' \
    -e 's|http://security.debian.org|https://security.debian.org|g' \
    /etc/apt/sources.list.d/debian.sources 2>/dev/null || true
RUN apt-get -o Acquire::Retries=5 update && apt-get install -y --no-install-recommends \
    libpq5 curl \
    && rm -rf /var/lib/apt/lists/*

# Непривилегированный пользователь
RUN useradd --create-home appuser

# Ставим wheels
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/* && rm -rf /wheels

# Копируем код сервиса
COPY . .

# Создаём папку для данных с правами для appuser
RUN mkdir -p /app/data && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

# Compose exposes the application through Nginx; trust its forwarded scheme/IP.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*"]
