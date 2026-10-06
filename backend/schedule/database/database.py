from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from pathlib import Path
from dotenv import load_dotenv

# Загружаем .env из корня проекта или текущей папки
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# --- ЛОГИКА ПЕРЕКЛЮЧЕНИЯ НА ЛОКАЛЬНУЮ БД ---
is_testing = os.getenv("TESTING") == "1"
# Если нет хоста или порта, считаем что работаем локально через SQLite
is_local = not DB_HOST or not DB_PORT

if is_testing:
    DATABASE_URL = "sqlite:///:memory:"
    print("🧪 Запуск в режиме ТЕСТИРОВАНИЯ (SQLite :memory:)")
elif is_local:
    # Создаем локальный файл БД в папке data
    db_path = Path(__file__).parent.parent / "data" / "schedule_local.db"
    db_path.parent.mkdir(exist_ok=True)
    DATABASE_URL = f"sqlite:///{db_path.absolute()}"
    print(f"🏠 Запуск в ЛОКАЛЬНОМ режиме (SQLite: {db_path.name})")
else:
    DATABASE_URL = URL.create(
        "postgresql+psycopg", username=DB_USER, password=DB_PASSWORD,
        host=DB_HOST, port=int(DB_PORT), database=DB_NAME,
    )
    print(f"🌐 Запуск в РЕЖИМЕ СЕРВЕРА (PostgreSQL: {DB_HOST})")

# Параметры подключения
engine_args = {"echo": os.getenv("DEBUG", "false").lower() == "true", "pool_pre_ping": True}
if isinstance(DATABASE_URL, str) and DATABASE_URL.startswith("sqlite"):
    engine_args["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **engine_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
