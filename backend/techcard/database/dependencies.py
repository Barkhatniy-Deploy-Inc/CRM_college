from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# ========== ПОДКЛЮЧЕНИЕ К PostgreSQL БД ТЕХКАРТ ==========

# Получаем параметры подключения из переменных окружения
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "techcard_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# Создаем URL подключения к PostgreSQL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Создаем движок для PostgreSQL
engine_techcard = create_engine(
    DATABASE_URL,
    echo=False,  # Отключаем логирование SQL в production
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600
)

SessionTechCardDB = sessionmaker(bind=engine_techcard)


# ========== ФУНКЦИИ ДЛЯ ПОЛУЧЕНИЯ СЕССИЙ БД ==========

# Получение сессии БД техкарт
async def get_techcard_db():
    db = SessionTechCardDB()
    try:
        yield db
    finally:
        db.close()
