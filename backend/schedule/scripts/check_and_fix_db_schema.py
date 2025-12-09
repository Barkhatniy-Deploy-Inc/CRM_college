import sys
sys.path.insert(0, '.')
from database.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='class_slots';"))
    cols = [r[0] for r in result]
    print('Columns in class_slots:', cols)

    if 'group_id' not in cols:
        print('Adding column group_id...')
        # Add column and FK
        conn.execute(text("ALTER TABLE class_slots ADD COLUMN group_id INTEGER;"))
        try:
            conn.execute(text("ALTER TABLE class_slots ADD CONSTRAINT fk_group FOREIGN KEY (group_id) REFERENCES groups(id);") )
            print('Foreign key constraint added for group_id')
        except Exception as e:
            print('Could not add FK constraint (maybe groups table missing or constraint exists):', e)
    else:
        print('group_id exists')

    if 'auditorium_id' not in cols:
        print('Adding column auditorium_id...')
        conn.execute(text("ALTER TABLE class_slots ADD COLUMN auditorium_id INTEGER;"))
        try:
            conn.execute(text("ALTER TABLE class_slots ADD CONSTRAINT fk_aud FOREIGN KEY (auditorium_id) REFERENCES auditoriums(id);") )
            print('Foreign key constraint added for auditorium_id')
        except Exception as e:
            print('Could not add FK constraint for auditorium_id:', e)
    else:
        print('auditorium_id exists')

    print('Done')
