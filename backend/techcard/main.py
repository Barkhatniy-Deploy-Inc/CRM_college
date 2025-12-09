from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.models_techcard import BaseTechCard
from database.dependencies import engine_techcard
from routers.techcard_router import router as techcard_router

# Создаём приложение FastAPI
app = FastAPI()

# Настройка CORS для работы с React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретный адрес React-приложения
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Создаём таблицы в БД техкарт (если их ещё нет)
BaseTechCard.metadata.create_all(bind=engine_techcard)

# Подключаем роутеры
app.include_router(techcard_router)

# Тестовый эндпоинт
@app.get("/")
async def root():
    return {"message": "API для генератора технологических карт работает!"}
