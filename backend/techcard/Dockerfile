# Stage 1: сборка бинарных зависимостей
FROM python:3.11-slim AS builder

WORKDIR /app

# Пакеты для сборки wheel (если есть бинарные зависимости)
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

# Копируем только requirements.txt
COPY requirements.txt .
# Сборка wheel-файлов (wheel — это компактные бинарные зависимости)
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# Stage 2: прод-рантайм
FROM python:3.11-slim AS runtime

WORKDIR /app

# Только реально нужные колёса (и Python без dev-зависимостей)
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

# Копируем финальный рабочий код (минимум)
COPY . .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
