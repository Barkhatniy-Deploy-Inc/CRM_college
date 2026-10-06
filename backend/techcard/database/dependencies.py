from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os

# Получаем абсолютный путь к папке database
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_DIR = os.path.join(BASE_DIR, "database")

TESTING = os.getenv("TESTING") == "1"
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("TECHCARD_DB_NAME", os.getenv("DB_NAME", "techcard_db"))

# ========== ПОДКЛЮЧЕНИЕ К БД ТЕХКАРТ ==========
# Приоритет: тесты (in-memory) → PostgreSQL (если задан DB_HOST) → локальный SQLite.
if TESTING:
    engine_techcard = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
elif DB_HOST:
    DATABASE_URL = URL.create(
        "postgresql+psycopg", username=DB_USER, password=DB_PASSWORD,
        host=DB_HOST, port=int(DB_PORT), database=DB_NAME,
    )
    engine_techcard = create_engine(
        DATABASE_URL,
        echo=DEBUG,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )
else:
    techcard_db_path = os.path.join(DATABASE_DIR, "techcards.db")
    engine_techcard = create_engine(
        f"sqlite:///{techcard_db_path}",
        connect_args={"check_same_thread": False},
        echo=DEBUG,
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
