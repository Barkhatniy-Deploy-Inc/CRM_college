from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from pathlib import Path
from dotenv import load_dotenv
from core.config import settings

load_dotenv()

# Определяем тип БД и строку подключения
if settings.DB_TYPE.lower() == "postgresql":
    # PostgreSQL подключение
    DATABASE_URL = f"postgresql+psycopg://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    engine_kwargs = {
        "echo": settings.DEBUG,  # SQL логи только в dev
        "pool_pre_ping": True,  # Проверка соединений перед использованием
        "pool_size": 10,
        "max_overflow": 20
    }
else:
    # SQLite для локальной разработки (по умолчанию)
    # Создаем директорию если её нет
    db_path = Path(settings.SQLITE_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    DATABASE_URL = f"sqlite:///{db_path.absolute()}"
    engine_kwargs = {
        "echo": settings.DEBUG,  # SQL логи только в dev
        "connect_args": {"check_same_thread": False}  # Для SQLite нужно отключить проверку потока
    }

# Создаем engine
engine = create_engine(DATABASE_URL, **engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency для получения сессии БД"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Инициализация БД - создание всех таблиц"""
    try:
        Base.metadata.create_all(bind=engine)
        print(f"✅ База данных инициализирована ({settings.DB_TYPE.upper()})")
        if settings.DB_TYPE.lower() == "sqlite":
            print(f"   SQLite файл: {Path(settings.SQLITE_PATH).absolute()}")
    except Exception as e:
        print(f"❌ Ошибка инициализации БД: {e}")
        raise
