from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Определяем директорию, где будет храниться файл БД
DATABASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_FILE = os.path.join(DATABASE_DIR, "auth.db")

# Строка подключения для SQLite
DATABASE_URL = f"sqlite:///{DATABASE_FILE}"

# echo=True оставим для отладки
engine = create_engine(DATABASE_URL, echo=True, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    # Эта команда создаст файл auth.db и все таблицы в нем
    Base.metadata.create_all(bind=engine)
