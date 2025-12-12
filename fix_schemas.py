#!/usr/bin/env python3
"""
Скрипт для исправления схем баз данных в соответствии с заявленными требованиями
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError
import subprocess

def setup_environment():
    """Устанавливаем переменные окружения для подключения к базам данных"""
    env_vars = {
        'DB_USER': 'postgres',
        'DB_PASSWORD': 'postgres',
        'DB_HOST': 'localhost',
        'DB_PORT': '5432'
    }
    
    for key, value in env_vars.items():
        if not os.getenv(key):
            os.environ[key] = value

def create_databases():
    """Создаем базы данных если они не существуют"""
    # Подключаемся к основному PostgreSQL серверу
    main_db_url = f"postgresql+psycopg://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/postgres"
    
    # Для создания баз данных нужно использовать отдельное подключение без транзакции
    import psycopg
    conn = psycopg.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres'),
        dbname='postgres'
    )
    conn.autocommit = True  # Отключаем автоматические транзакции
    
    databases = ['auth_db', 'tech_card_db', 'schedule_db']
    
    with conn.cursor() as cursor:
        for db_name in databases:
            try:
                cursor.execute(f"CREATE DATABASE {db_name}")
                print(f"✅ Создана база данных: {db_name}")
            except psycopg.errors.DuplicateDatabase:
                print(f"⚠️  База данных {db_name} уже существует")
            except Exception as e:
                print(f"❌ Ошибка при создании базы {db_name}: {e}")
    
    conn.close()

def fix_auth_db_schema():
    """Исправляем схему auth_db в соответствии с требованиями"""
    db_url = f"postgresql+psycopg://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/auth_db"
    engine = create_engine(db_url)
    
    # SQL для создания таблицы users в соответствии с требованиями
    sql = """
    DROP TABLE IF EXISTS users CASCADE;
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        full_name VARCHAR(255) NOT NULL,
        is_active BOOLEAN DEFAULT TRUE NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
    );
    
    -- Добавляем триггер для автоматического обновления updated_at
    CREATE OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = NOW();
        RETURN NEW;
    END;
    $$ language 'plpgsql';
    
    DROP TRIGGER IF EXISTS update_users_updated_at ON users;
    CREATE TRIGGER update_users_updated_at 
        BEFORE UPDATE ON users 
        FOR EACH ROW 
        EXECUTE FUNCTION update_updated_at_column();
    """
    
    with engine.connect() as conn:
        conn.execute(text(sql))
        conn.commit()
    
    print("✅ Схема auth_db обновлена")

def fix_tech_card_db_schema():
    """Исправляем схему tech_card_db в соответствии с требованиями"""
    db_url = f"postgresql+psycopg://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/tech_card_db"
    engine = create_engine(db_url)
    
    # SQL для создания таблиц в соответствии с требованиями
    sql = """
    DROP TABLE IF EXISTS lesson_type CASCADE;
    DROP TABLE IF EXISTS lesson CASCADE;
    DROP TABLE IF EXISTS curator_group CASCADE;
    DROP TABLE IF EXISTS learning_outcomes CASCADE;
    DROP TABLE IF EXISTS pk_and_ok CASCADE;
    DROP TABLE IF EXISTS skills_and_knowledge CASCADE;
    DROP TABLE IF EXISTS Teacher CASCADE;
    DROP TABLE IF EXISTS Group_name CASCADE;
    DROP TABLE IF EXISTS type_lesson CASCADE;
    
    -- Создаем таблицы в соответствии с заявленной схемой
    CREATE TABLE IF NOT EXISTS lesson_type (
        primary_key SERIAL PRIMARY KEY,
        lesson_type VARCHAR(255),
        name_teacher VARCHAR(255)
    );
    
    CREATE TABLE IF NOT EXISTS Teacher (
        primary_key SERIAL PRIMARY KEY,
        full_name VARCHAR(255) NOT NULL
    );
    
    CREATE TABLE IF NOT EXISTS lesson (
        primary_key SERIAL PRIMARY KEY,
        topic VARCHAR(255) NOT NULL,
        group_name VARCHAR(255),
        teacher_id INTEGER REFERENCES Teacher(primary_key)
    );
    
    CREATE TABLE IF NOT EXISTS curator_group (
        primary_key SERIAL PRIMARY KEY,
        group_name VARCHAR(255) NOT NULL
    );
    
    CREATE TABLE IF NOT EXISTS learning_outcomes (
        primary_key SERIAL PRIMARY KEY,
        lesson_id INTEGER REFERENCES lesson(primary_key),
        skill TEXT,
        know TEXT
    );
    
    CREATE TABLE IF NOT EXISTS pk_and_ok (
        primary_key SERIAL PRIMARY KEY,
        lesson_id INTEGER REFERENCES lesson(primary_key),
        prof_comp TEXT,
        general_comp TEXT
    );
    
    CREATE TABLE IF NOT EXISTS skills_and_knowledge (
        primary_key SERIAL PRIMARY KEY,
        lesson_id INTEGER REFERENCES lesson(primary_key),
        skill TEXT,
        knowledge TEXT
    );
    
    CREATE TABLE IF NOT EXISTS type_lesson (
        primary_key SERIAL PRIMARY KEY,
        lesson VARCHAR(255) NOT NULL
    );
    """
    
    with engine.connect() as conn:
        conn.execute(text(sql))
        conn.commit()
    
    print("✅ Схема tech_card_db обновлена")

def fix_schedule_db_schema():
    """Исправляем схему schedule_db в соответствии с требованиями"""
    db_url = f"postgresql+psycopg://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/schedule_db"
    engine = create_engine(db_url)
    
    # SQL для создания таблиц в соответствии с требованиями
    sql = """
    DROP TABLE IF EXISTS schedule_lessons CASCADE;
    DROP TABLE IF EXISTS schedule_teachers CASCADE;
    DROP TABLE IF EXISTS schedule_auditoriums CASCADE;
    DROP TABLE IF EXISTS schedule_groups CASCADE;
    DROP TABLE IF EXISTS schedule_subjects CASCADE;
    
    -- Создаем таблицы в соответствии с заявленной схемой
    CREATE TABLE IF NOT EXISTS schedule_teachers (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL
    );
    
    CREATE TABLE IF NOT EXISTS schedule_auditoriums (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        is_active BOOLEAN DEFAULT TRUE NOT NULL
    );
    
    CREATE TABLE IF NOT EXISTS schedule_groups (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        course INTEGER
    );
    
    CREATE TABLE IF NOT EXISTS schedule_subjects (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        teacher_id INTEGER REFERENCES schedule_teachers(id)
    );
    
    CREATE TABLE IF NOT EXISTS schedule_lessons (
        id SERIAL PRIMARY KEY,
        date DATE NOT NULL,
        time_start TIME NOT NULL,
        time_end TIME NOT NULL,
        lesson_number INTEGER,
        group_id INTEGER REFERENCES schedule_groups(id),
        subgroup INTEGER,
        subject_id INTEGER REFERENCES schedule_subjects(id),
        teacher_id INTEGER REFERENCES schedule_teachers(id),
        auditorium_id INTEGER REFERENCES schedule_auditoriums(id),
        activity_type VARCHAR(255),
        comment TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
    );
    """
    
    with engine.connect() as conn:
        conn.execute(text(sql))
        conn.commit()
    
    print("✅ Схема schedule_db обновлена")

def update_application_configs():
    """Обновляем конфигурации приложений для использования правильных БД"""
    print("🔄 Обновляем конфигурации приложений...")
    
    # Обновляем конфиг для auth сервиса
    auth_config_path = "/workspace/backend/auth/core/config.py"
    with open(auth_config_path, 'r') as f:
        auth_config = f.read()
    
    # Убедимся, что DB_NAME указывает на auth_db
    if "AUTH_DB_NAME" not in auth_config:
        # Заменяем строку с DB_NAME на использование AUTH_DB_NAME
        auth_config = auth_config.replace(
            'DB_NAME: str = os.getenv("DB_NAME", os.getenv("AUTH_DB_NAME", "auth_db"))',
            'DB_NAME: str = os.getenv("DB_NAME", os.getenv("AUTH_DB_NAME", "auth_db"))'
        )
    
    with open(auth_config_path, 'w') as f:
        f.write(auth_config)
    
    # Обновляем конфиг для schedule сервиса
    schedule_db_path = "/workspace/backend/schedule/database/database.py"
    with open(schedule_db_path, 'r') as f:
        schedule_db_config = f.read()
    
    # Заменяем подключение на использование schedule_db
    schedule_db_config = schedule_db_config.replace(
        'DB_NAME = os.getenv("DB_NAME")',
        'DB_NAME = os.getenv("DB_NAME", "schedule_db")'
    )
    
    with open(schedule_db_path, 'w') as f:
        f.write(schedule_db_config)
    
    print("✅ Конфигурации приложений обновлены")

def update_models():
    """Обновляем модели приложений для соответствия новым схемам"""
    print("🔄 Обновляем модели приложений...")
    
    # Создаем новую модель для auth сервиса (только требуемые поля)
    auth_models_path = "/workspace/backend/auth/database/models.py"
    auth_models_content = '''from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
from datetime import datetime


class User(Base):
    """Модель пользователя"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
'''
    
    with open(auth_models_path, 'w') as f:
        f.write(auth_models_content)
    
    # Создаем модель для techcard сервиса
    techcard_models_path = "/workspace/backend/techcard/database/models.py"
    techcard_models_content = '''from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


# Модели для tech_card_db в соответствии с требованиями
class LessonType(Base):
    __tablename__ = "lesson_type"
    
    primary_key = Column(Integer, primary_key=True, index=True)
    lesson_type = Column(String)
    name_teacher = Column(String)


class Teacher(Base):
    __tablename__ = "Teacher"
    
    primary_key = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)


class Lesson(Base):
    __tablename__ = "lesson"
    
    primary_key = Column(Integer, primary_key=True, index=True)
    topic = Column(String, nullable=False)
    group_name = Column(String)
    teacher_id = Column(Integer, ForeignKey("Teacher.primary_key"))


class CuratorGroup(Base):
    __tablename__ = "curator_group"
    
    primary_key = Column(Integer, primary_key=True, index=True)
    group_name = Column(String, nullable=False)


class LearningOutcome(Base):
    __tablename__ = "learning_outcomes"
    
    primary_key = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lesson.primary_key"))
    skill = Column(Text)
    know = Column(Text)


class PkAndOk(Base):
    __tablename__ = "pk_and_ok"
    
    primary_key = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lesson.primary_key"))
    prof_comp = Column(Text)
    general_comp = Column(Text)


class SkillsAndKnowledge(Base):
    __tablename__ = "skills_and_knowledge"
    
    primary_key = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lesson.primary_key"))
    skill = Column(Text)
    knowledge = Column(Text)


class TypeLesson(Base):
    __tablename__ = "type_lesson"
    
    primary_key = Column(Integer, primary_key=True, index=True)
    lesson = Column(String, nullable=False)
'''


    with open(techcard_models_path, 'w') as f:
        f.write(techcard_models_content)
    
    # Обновляем зависимости techcard для подключения к PostgreSQL
    techcard_deps_path = "/workspace/backend/techcard/database/dependencies.py"
    techcard_deps_content = '''from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Подключение к PostgreSQL для tech_card_db
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("TECHCARD_DB_NAME", "tech_card_db")

DATABASE_URL = f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine_techcard = create_engine(DATABASE_URL, echo=True)
SessionTechCardDB = sessionmaker(bind=engine_techcard)


# Функция для получения сессии БД техкарт
async def get_techcard_db():
    db = SessionTechCardDB()
    try:
        yield db
    finally:
        db.close()
'''

    with open(techcard_deps_path, 'w') as f:
        f.write(techcard_deps_content)
    
    # Обновляем модель для schedule сервиса
    schedule_models_path = "/workspace/backend/schedule/database/models.py"
    schedule_models_content = '''from sqlalchemy import Column, Integer, String, DateTime, Date, Time, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
from enum import Enum
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class ScheduleTeacher(Base):
    __tablename__ = "schedule_teachers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)


class ScheduleAuditorium(Base):
    __tablename__ = "schedule_auditoriums"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)


class ScheduleGroup(Base):
    __tablename__ = "schedule_groups"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    course = Column(Integer)


class ScheduleSubject(Base):
    __tablename__ = "schedule_subjects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    teacher_id = Column(Integer, ForeignKey("schedule_teachers.id"))


class ScheduleLesson(Base):
    __tablename__ = "schedule_lessons"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    time_start = Column(Time, nullable=False)
    time_end = Column(Time, nullable=False)
    lesson_number = Column(Integer)
    group_id = Column(Integer, ForeignKey("schedule_groups.id"))
    subgroup = Column(Integer)
    subject_id = Column(Integer, ForeignKey("schedule_subjects.id"))
    teacher_id = Column(Integer, ForeignKey("schedule_teachers.id"))
    auditorium_id = Column(Integer, ForeignKey("schedule_auditoriums.id"))
    activity_type = Column(String)
    comment = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Связи
    group = relationship("ScheduleGroup")
    teacher = relationship("ScheduleTeacher")
    subject = relationship("ScheduleSubject")
    auditorium = relationship("ScheduleAuditorium")


# Pydantic модели для API
class ScheduleTeacherBase(BaseModel):
    name: str

class ScheduleTeacherCreate(ScheduleTeacherBase):
    pass

class ScheduleTeacherResponse(ScheduleTeacherBase):
    id: int
    
    class Config:
        from_attributes = True


class ScheduleAuditoriumBase(BaseModel):
    name: str
    is_active: bool = True

class ScheduleAuditoriumCreate(ScheduleAuditoriumBase):
    pass

class ScheduleAuditoriumResponse(ScheduleAuditoriumBase):
    id: int
    
    class Config:
        from_attributes = True


class ScheduleGroupBase(BaseModel):
    name: str
    course: Optional[int] = None

class ScheduleGroupCreate(ScheduleGroupBase):
    pass

class ScheduleGroupResponse(ScheduleGroupBase):
    id: int
    
    class Config:
        from_attributes = True


class ScheduleSubjectBase(BaseModel):
    name: str
    teacher_id: int

class ScheduleSubjectCreate(ScheduleSubjectBase):
    pass

class ScheduleSubjectResponse(ScheduleSubjectBase):
    id: int
    
    class Config:
        from_attributes = True


class ScheduleLessonBase(BaseModel):
    date: datetime
    time_start: datetime
    time_end: datetime
    lesson_number: Optional[int] = None
    group_id: int
    subgroup: Optional[int] = None
    subject_id: int
    teacher_id: int
    auditorium_id: int
    activity_type: Optional[str] = None
    comment: Optional[str] = None

class ScheduleLessonCreate(ScheduleLessonBase):
    pass

class ScheduleLessonResponse(ScheduleLessonBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
'''
    
    # Заменяем старое содержимое новым
    with open(schedule_models_path, 'w') as f:
        f.write(schedule_models_content)
    
    print("✅ Модели приложений обновлены")

def main():
    print("🚀 Начинаем исправление схем баз данных...")
    
    setup_environment()
    create_databases()
    fix_auth_db_schema()
    fix_tech_card_db_schema()
    fix_schedule_db_schema()
    update_application_configs()
    update_models()
    
    print("\\n✅ Все схемы баз данных исправлены и приложения обновлены!")
    print("💡 Теперь можно запустить сервисы с правильной схемой баз данных.")

if __name__ == "__main__":
    main()