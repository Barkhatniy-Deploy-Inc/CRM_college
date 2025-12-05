import sqlite3
import os
from contextlib import contextmanager

DATABASE_PATH = os.getenv("DATABASE_PATH", "./database.db")


@contextmanager
def get_db():
    """Context manager для подключения к БД"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Инициализация базы данных с созданием всех необходимых таблиц и индексов"""
    with get_db() as conn:
        cursor = conn.cursor()

        cursor.execute("PRAGMA foreign_keys = ON;")

        # Таблица пользователей
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                telegram_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Таблица курсов
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                instructor TEXT,
                start_date TEXT,
                end_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Новая таблица аудиторий
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS auditoriums (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                capacity INTEGER,
                description TEXT
            )
        """)

        # Обновленная таблица слотов (занятий)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS class_slots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER NOT NULL,
                auditorium_id INTEGER,
                title TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                instructor TEXT,
                max_participants INTEGER,
                status TEXT DEFAULT 'scheduled',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
                FOREIGN KEY (auditorium_id) REFERENCES auditoriums(id) ON DELETE SET NULL
            )
        """)

        # Таблица участников
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS participants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_slot_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                status TEXT DEFAULT 'registered',
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(class_slot_id, user_id),
                FOREIGN KEY (class_slot_id) REFERENCES class_slots(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # --- Индексы для ускорения запросов ---
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_auditoriums_name ON auditoriums (name);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_class_slots_course_id ON class_slots (course_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_class_slots_auditorium_id ON class_slots (auditorium_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_class_slots_start_time ON class_slots (start_time);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_participants_user_id ON participants (user_id);")

        print("✅ База данных инициализирована, индексы созданы.")

        # Простая миграция: попытка перенести старые 'location' в новую таблицу
        try:
            cursor.execute("SELECT location FROM class_slots_old")
            print("⚠️  Обнаружена старая схема. Попытка миграции данных...")
            # Логику миграции можно добавить здесь, но для простоты мы ее опустим.
            # Сейчас просто переименуем старую таблицу, чтобы избежать конфликтов.
            cursor.execute("ALTER TABLE class_slots RENAME TO class_slots_old_migrated")
            print("✅ Старая таблица слотов переименована. Создайте новую структуру.")
        except sqlite3.OperationalError:
            # Если class_slots_old не существует, все в порядке
            pass
