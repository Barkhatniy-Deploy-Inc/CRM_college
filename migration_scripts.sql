-- Миграции для приведения схем БД к коду приложения

-- 1. auth_db: Добавление недостающих полей в таблицу users
-- (если использовать подход "код как истина")
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT FALSE NOT NULL;
ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(20) DEFAULT 'student' NOT NULL;
ALTER TABLE users ADD COLUMN IF NOT EXISTS failed_login_attempts INTEGER DEFAULT 0 NOT NULL;
ALTER TABLE users ADD COLUMN IF NOT EXISTS locked_until TIMESTAMP WITH TIME ZONE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login TIMESTAMP WITH TIME ZONE;

-- 2. tech_card_db: Создание корректной структуры таблиц
-- Удаление старых таблиц (если они существуют и были созданы вручную)
/*
DROP TABLE IF EXISTS lesson_type CASCADE;
DROP TABLE IF EXISTS primary_key CASCADE;
DROP TABLE IF EXISTS curator_group CASCADE;
DROP TABLE IF EXISTS group_name CASCADE;
DROP TABLE IF EXISTS learning_outcomes CASCADE;
DROP TABLE IF EXISTS pk_and_ok CASCADE;
DROP TABLE IF EXISTS skills_and_knowledge CASCADE;
DROP TABLE IF EXISTS lesson CASCADE;
*/

-- Создание таблиц в соответствии с кодовыми моделями
CREATE TABLE IF NOT EXISTS tech_cards (
    id SERIAL PRIMARY KEY,
    group_id INTEGER,
    lesson_id INTEGER,
    teacher_id INTEGER,
    lesson_type_id INTEGER,
    tema TEXT NOT NULL,
    nomer_zanyatiya VARCHAR(50),
    ped_tech TEXT,
    cel_zanyatiya TEXT,
    zadachi_obuch TEXT,
    zadachi_razv TEXT,
    zadachi_vosp TEXT,
    prognoz_result TEXT,
    oborudovanie TEXT,
    istochniki TEXT
);

CREATE TABLE IF NOT EXISTS tech_card_stages (
    id SERIAL PRIMARY KEY,
    tech_card_id INTEGER NOT NULL REFERENCES tech_cards(id) ON DELETE CASCADE,
    nomer_etapa INTEGER NOT NULL,
    nazvanie_etapa VARCHAR(255) NOT NULL,
    cel_etapa TEXT,
    dlitelnost VARCHAR(50),
    deyatelnost_prepod TEXT,
    deyatelnost_obuch TEXT,
    formiruemye_kompetencii TEXT
);

-- 3. schedule_db: Создание таблиц в соответствии с кодом приложения
-- Удаление старых таблиц (если они существуют)
/*
DROP TABLE IF EXISTS schedule_teachers CASCADE;
DROP TABLE IF EXISTS schedule_auditoriums CASCADE;
DROP TABLE IF EXISTS schedule_groups CASCADE;
DROP TABLE IF EXISTS schedule_subjects CASCADE;
DROP TABLE IF EXISTS schedule_lessons CASCADE;
*/

-- Создание таблиц в соответствии с моделями
CREATE TABLE IF NOT EXISTS schedule_auditoriums (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    capacity INTEGER,
    description VARCHAR(500)
);

CREATE TABLE IF NOT EXISTS schedule_groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    instructor VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS schedule_class_slots (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    instructor VARCHAR(255),
    max_participants INTEGER,
    status VARCHAR(20) DEFAULT 'scheduled',
    group_id INTEGER REFERENCES schedule_groups(id),
    auditorium_id INTEGER REFERENCES schedule_auditoriums(id)
);

-- 4. Если же использовать подход "схема как истина", то нужно изменить модели:
-- Ниже приведены примеры обновленных моделей для schedule_db:

/*
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Date, Time, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

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
    course = Column(Integer, nullable=False)  # Новое поле

class ScheduleSubject(Base):
    __tablename__ = "schedule_subjects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    teacher_id = Column(Integer, ForeignKey("schedule_teachers.id"), nullable=False)

class ScheduleLesson(Base):
    __tablename__ = "schedule_lessons"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    time_start = Column(Time, nullable=False)
    time_end = Column(Time, nullable=False)
    lesson_number = Column(Integer, nullable=False)
    group_id = Column(Integer, ForeignKey("schedule_groups.id"), nullable=False)
    subgroup = Column(String, nullable=True)  # Новое поле
    subject_id = Column(Integer, ForeignKey("schedule_subjects.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("schedule_teachers.id"), nullable=False)
    auditorium_id = Column(Integer, ForeignKey("schedule_auditoriums.id"), nullable=False)
    activity_type = Column(String, nullable=True)  # Новое поле
    comment = Column(String, nullable=True)  # Новое поле
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)  # Новое поле
*/