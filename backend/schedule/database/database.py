from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# --- ВРЕМЕННАЯ ОТЛАДКА ---
print("--- DEBUG: DATABASE CONNECTION ---")
print(f"USER: {DB_USER}")
print(f"PASSWORD: {'*' * len(DB_PASSWORD) if DB_PASSWORD else 'NOT FOUND'}")
print(f"HOST: {DB_HOST}")
print(f"PORT: {DB_PORT}")
print(f"NAME: {DB_NAME}")
print("---------------------------------")
# ---------------------------

# Используем новый драйвер psycopg (вместо psycopg2)
DATABASE_URL = f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Добавляем echo=True, чтобы видеть все SQL-запросы в консоли
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    # Эта команда создаст все таблицы, определенные в models.py
    Base.metadata.create_all(bind=engine)
