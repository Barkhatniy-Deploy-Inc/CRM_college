# backend/auth/main.py
import logging
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn

from core.config import settings
from middleware.rate_limit import RateLimitMiddleware
from routers import auth, users
from database.database import engine, Base

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Безопасное создание таблиц БД при старте
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title=settings.APP_NAME, 
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
if settings.RATE_LIMIT_ENABLED:
    app.add_middleware(RateLimitMiddleware)

# Health check
@app.get("/api/auth/health", tags=["⚙️ Система"])
async def health_check():
    return {"status": "healthy", "service": "Auth Service"}

# Подключение роутеров с явными префиксами
app.include_router(auth.router, prefix="/api/auth")
app.include_router(users.router, prefix="/api/users")

@app.get("/")
async def root():
    return {"service": settings.APP_NAME, "version": settings.APP_VERSION}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
