"""
Скрипт для инициализации базовых разрешений в системе
"""
from sqlalchemy.orm import Session
from database.database import SessionLocal, init_db
from database.models import Permission, User, UserRole


def create_default_permissions(db: Session):
    """Создание базовых разрешений"""
    permissions = [
        # Расписание
        {"name": "schedule:read", "description": "Просмотр расписания", "resource": "schedule", "action": "read"},
        {"name": "schedule:create", "description": "Создание расписания", "resource": "schedule", "action": "create"},
        {"name": "schedule:update", "description": "Обновление расписания", "resource": "schedule", "action": "update"},
        {"name": "schedule:delete", "description": "Удаление расписания", "resource": "schedule", "action": "delete"},
        
        # Аудитории
        {"name": "auditoriums:read", "description": "Просмотр аудиторий", "resource": "auditoriums", "action": "read"},
        {"name": "auditoriums:create", "description": "Создание аудиторий", "resource": "auditoriums", "action": "create"},
        {"name": "auditoriums:update", "description": "Обновление аудиторий", "resource": "auditoriums", "action": "update"},
        {"name": "auditoriums:delete", "description": "Удаление аудиторий", "resource": "auditoriums", "action": "delete"},
        
        # Группы
        {"name": "groups:read", "description": "Просмотр групп", "resource": "groups", "action": "read"},
        {"name": "groups:create", "description": "Создание групп", "resource": "groups", "action": "create"},
        {"name": "groups:update", "description": "Обновление групп", "resource": "groups", "action": "update"},
        {"name": "groups:delete", "description": "Удаление групп", "resource": "groups", "action": "delete"},
        
        # Пользователи
        {"name": "users:read", "description": "Просмотр пользователей", "resource": "users", "action": "read"},
        {"name": "users:create", "description": "Создание пользователей", "resource": "users", "action": "create"},
        {"name": "users:update", "description": "Обновление пользователей", "resource": "users", "action": "update"},
        {"name": "users:delete", "description": "Удаление пользователей", "resource": "users", "action": "delete"},
        
        # Техкарты
        {"name": "techcards:read", "description": "Просмотр техкарт", "resource": "techcards", "action": "read"},
        {"name": "techcards:create", "description": "Создание техкарт", "resource": "techcards", "action": "create"},
        {"name": "techcards:update", "description": "Обновление техкарт", "resource": "techcards", "action": "update"},
        {"name": "techcards:delete", "description": "Удаление техкарт", "resource": "techcards", "action": "delete"},
    ]
    
    created_count = 0
    for perm_data in permissions:
        existing = db.query(Permission).filter(Permission.name == perm_data["name"]).first()
        if not existing:
            permission = Permission(**perm_data)
            db.add(permission)
            created_count += 1
        else:
            print(f"Разрешение {perm_data['name']} уже существует")
    
    db.commit()
    print(f"✅ Создано {created_count} новых разрешений")


def create_admin_user(db: Session, email: str, password: str, full_name: str = "Администратор"):
    """Создание администратора"""
    from services.user_service import create_user
    from database.schemas import UserCreate
    
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        print(f"⚠️ Пользователь {email} уже существует")
        return
    
    user_data = UserCreate(
        email=email,
        password=password,
        full_name=full_name,
        role=UserRole.ADMIN
    )
    
    user = create_user(user_data, db)
    user.is_verified = True
    db.commit()
    
    print(f"✅ Создан администратор: {email}")


if __name__ == "__main__":
    import sys
    
    # Инициализация БД
    init_db()
    
    db = SessionLocal()
    try:
        # Создание разрешений
        print("📝 Создание разрешений...")
        create_default_permissions(db)
        
        # Создание администратора (если указаны параметры)
        if len(sys.argv) >= 3:
            email = sys.argv[1]
            password = sys.argv[2]
            full_name = sys.argv[3] if len(sys.argv) > 3 else "Администратор"
            print(f"\n👤 Создание администратора...")
            create_admin_user(db, email, password, full_name)
        else:
            print("\n💡 Для создания администратора запустите:")
            print("python init_permissions.py admin@example.com password123 'Имя Администратора'")
        
    finally:
        db.close()

