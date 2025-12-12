# Анализ соответствия схем БД и кода приложения

## Краткий список найденных проблем:

### 1. База auth_db
- В модели User есть дополнительные поля, не указанные в схеме: is_verified, role, failed_login_attempts, locked_until, last_login
- Все эти поля логически обоснованы и могут быть добавлены в схему

### 2. База tech_card_db  
- Полное несоответствие между заявленной схемой и фактическими моделями
- Заявленная схема содержит дублирующиеся и плохо структурированные таблицы
- Кодовая модель использует нормализованную структуру с двумя связанными таблицами

### 3. База schedule_db
- Не соответствуют названия таблиц и структура
- В коде отсутствуют отдельные таблицы для преподавателей и предметов
- Используется другая структура связей между сущностями

## Подробные исправления:

### 1. auth_db - Добавление недостающих полей в документацию схемы

-- Дополнительные поля в таблице users
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT FALSE NOT NULL;
ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(20) DEFAULT 'student' NOT NULL;
ALTER TABLE users ADD COLUMN IF NOT EXISTS failed_login_attempts INTEGER DEFAULT 0 NOT NULL;
ALTER TABLE users ADD COLUMN IF NOT EXISTS locked_until TIMESTAMP WITH TIME ZONE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login TIMESTAMP WITH TIME ZONE;

### 2. tech_card_db - Переработка структуры таблиц

-- Удаление старых таблиц (если существуют)
-- DROP TABLE IF EXISTS lesson_type, primary_key, curator_group, group_name, learning_outcomes, pk_and_ok, skills_and_knowledge, lesson;

-- Создание правильной структуры на основе моделей
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

-- Альтернативно: изменение моделей под требуемую схему (если схема является эталоном)
-- В этом случае нужно создать отдельные модели для каждой из таблиц, указанных в схеме

### 3. schedule_db - Синхронизация схемы и кода

-- Создание таблиц в соответствии с кодовой моделью
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

-- Альтернативно: изменение моделей под требуемую схему
-- Ниже представлены корректные модели для соответствия схеме из задания:

"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Date, Time, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

# Таблицы для расписания
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
    course = Column(Integer, nullable=False)

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
    subgroup = Column(String, nullable=True)
    subject_id = Column(Integer, ForeignKey("schedule_subjects.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("schedule_teachers.id"), nullable=False)
    auditorium_id = Column(Integer, ForeignKey("schedule_auditoriums.id"), nullable=False)
    activity_type = Column(String, nullable=True)
    comment = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
"""

-- Создание внешних ключей для обеспечения целостности
ALTER TABLE schedule_subjects ADD CONSTRAINT fk_schedule_subjects_teacher FOREIGN KEY (teacher_id) REFERENCES schedule_teachers(id);
ALTER TABLE schedule_lessons ADD CONSTRAINT fk_schedule_lessons_group FOREIGN KEY (group_id) REFERENCES schedule_groups(id);
ALTER TABLE schedule_lessons ADD CONSTRAINT fk_schedule_lessons_subject FOREIGN KEY (subject_id) REFERENCES schedule_subjects(id);
ALTER TABLE schedule_lessons ADD CONSTRAINT fk_schedule_lessons_teacher FOREIGN KEY (teacher_id) REFERENCES schedule_teachers(id);
ALTER TABLE schedule_lessons ADD CONSTRAINT fk_schedule_lessons_auditorium FOREIGN KEY (auditorium_id) REFERENCES schedule_auditoriums(id);

## Рекомендации:

1. Для auth_db: рекомендуется обновить документацию схемы, чтобы отразить все дополнительные поля в таблице users.

2. Для tech_card_db: требуется принять решение о том, какая структура является эталонной. На мой взгляд, текущая кодовая модель более правильно спроектирована, чем описанная схема.

3. Для schedule_db: рекомендуется либо обновить модели под требуемую схему (предпочтительно для согласования с описанием), либо обновить схему под текущие модели.

4. Важно также рассмотреть возможность использования миграционного инструмента (например, Alembic) для управления изменениями схемы в будущем.