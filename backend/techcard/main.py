import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.models_techcard import BaseTechCard
from database.dependencies import engine_techcard
from routers.techcard_router import router as techcard_router

# Создаём приложение FastAPI
app = FastAPI(
    title="Генератор технологических карт",
    version="1.0.0",
    description="API для создания и управления технологическими картами"
)

# Безопасная настройка CORS
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "Origin", "X-Requested-With"],
)

# Создаём таблицы в БД техкарт (если их ещё нет)
BaseTechCard.metadata.create_all(bind=engine_techcard)

# Подключаем роутеры
app.include_router(techcard_router)

# Тестовый эндпоинт
@app.get("/")
async def root():
    return {"message": "API для генератора технологических карт работает!"}

# Health check endpoint
@app.get("/api/health", tags=["🏥 Health"])
async def health_check():
    """Health check endpoint для мониторинга"""
    from datetime import datetime, timezone
    return {
        "status": "healthy",
        "service": "techcard-api",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
