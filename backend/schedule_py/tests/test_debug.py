import sys
import os

# Убедимся, что используется тестовая БД
os.environ["DATABASE_PATH"] = "test_database.db"

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.database import get_db, init_db
import sqlite3


def test_direct_database_write():
    """Прямая проверка записи в БД без API."""
    print("\n" + "=" * 60)
    print("🔍 ОТЛАДКА: Прямая запись в БД")
    print("=" * 60)

    # Инициализируем БД
    init_db()

    # Очищаем таблицу
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM auditoriums")
        print("✅ Таблица auditoriums очищена")

    # Проверяем, что пустая
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM auditoriums")
        rows = cursor.fetchall()
        print(f"📊 Записей в БД ПОСЛЕ очистки: {len(rows)}")
        assert len(rows) == 0, f"БД не пустая: {rows}"

    # Вставляем запись
    print("\n📝 Вставляем запись...")
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO auditoriums (name, capacity, description) VALUES (?, ?, ?)",
            ("Test Auditorium", 50, "Test Description")
        )
        new_id = cursor.lastrowid
        print(f"✅ Вставлена запись с ID: {new_id}")

    # Проверяем, что записалась
    print("\n🔎 Проверяем, что запись сохранилась...")
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM auditoriums")
        rows = cursor.fetchall()
        print(f"📊 Записей в БД ПОСЛЕ вставки: {len(rows)}")

        if rows:
            for row in rows:
                print(f"   → ID: {row['id']}, Name: {row['name']}, Capacity: {row['capacity']}")
        else:
            print("   ❌ ПРОБЛЕМА: БД пустая после вставки!")

        assert len(rows) == 1, f"Ожидалась 1 запись, найдено: {len(rows)}"

    print("\n" + "=" * 60)
    print("✅ ТЕСТ ПРОЙДЕН: Прямая запись в БД работает")
    print("=" * 60 + "\n")


def test_database_path():
    """Проверка, что используется правильный путь к БД."""
    from database.database import DATABASE_PATH
    print(f"\n📂 Путь к БД: {DATABASE_PATH}")
    print(f"📂 Абсолютный путь: {os.path.abspath(DATABASE_PATH)}")

    # Проверяем, что файл существует
    if os.path.exists(DATABASE_PATH):
        size = os.path.getsize(DATABASE_PATH)
        print(f"💾 Размер файла БД: {size} байт")
    else:
        print("❌ Файл БД не существует!")

    assert DATABASE_PATH == "test_database.db", f"Неправильный путь к БД: {DATABASE_PATH}"
