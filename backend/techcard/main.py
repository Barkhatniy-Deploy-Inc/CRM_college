from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
import os
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database.dependencies import engine_techcard
from database.models_techcard import BaseTechCard
from routers.techcard_router import router as techcard_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Безопасное создание таблиц при старте
    BaseTechCard.metadata.create_all(bind=engine_techcard)
    yield

app = FastAPI(title="Techcard Service", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:8080").split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Глобальный Health Check (ПОЛНЫЙ ПУТЬ)
@app.get("/api/techcard/health", tags=["⚙️ Система"])
def health_check():
    try:
        with engine_techcard.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return JSONResponse(status_code=503, content={"status": "unhealthy", "service": "Techcard Service"})
    return {"status": "healthy", "service": "Techcard Service"}

# Подключение роутеров без префикса в include (префикс задан в самом роутере)
app.include_router(techcard_router)

@app.get("/")
async def root():
    return {"message": "API для генератора технологических карт работает!"}
