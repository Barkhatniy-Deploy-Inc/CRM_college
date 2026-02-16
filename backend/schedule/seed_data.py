from database.database import SessionLocal
from sqlalchemy import text
from datetime import datetime, timedelta

def seed():
    db = SessionLocal()
    try:
        # 1. Получаем ID группы
        res = db.execute(text("SELECT id FROM groups WHERE name = 'ИСП-21' LIMIT 1"))
        row = res.fetchone()
        if not row:
            print("Группа ИСП-21 не найдена")
            return
        group_id = row[0]

        # 2. Получаем ID аудиторий
        res = db.execute(text("SELECT id FROM auditoriums LIMIT 4"))
        aud_ids = [r[0] for r in res.fetchall()]

        subjects = ['Математика', 'Программирование Python', 'Базы данных', 'Физкультура', 'Английский язык']
        teachers = ['Иванов И.И.', 'Петров П.П.', 'Сидорова С.С.', 'Борисов Б.Б.', 'Уайт У.']

        start_date = datetime(2026, 2, 16)
        print(f"Начинаем загрузку расписания для группы ID:{group_id}...")

        for i in range(6):
            current_day = start_date + timedelta(days=i)
            for j in range(3):
                start_time = current_day.replace(hour=[8, 10, 12][j], minute=[30, 10, 10][j])
                end_time = current_day.replace(hour=[10, 11, 13][j], minute=[0, 40, 40][j])
                
                # Используем строчное значение 'scheduled' для Enum
                db.execute(text("""
                    INSERT INTO class_slots (title, start_time, end_time, instructor, status, group_id, auditorium_id)
                    VALUES (:t, :s, :e, :i, 'scheduled', :g, :a)
                """), {
                    't': subjects[(i+j) % len(subjects)],
                    's': start_time,
                    'e': end_time,
                    'i': teachers[(i+j) % len(teachers)],
                    'g': group_id,
                    'a': aud_ids[(i+j) % len(aud_ids)]
                })
        
        db.commit()
        print("✅ Расписание успешно загружено!")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
