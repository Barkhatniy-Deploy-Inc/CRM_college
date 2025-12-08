from ics import Calendar, Event
from datetime import datetime
from sqlalchemy.orm import Session
from database.models import ClassSlot
from api.schedule_api import get_schedule_list

async def generate_calendar_for_user(user_id: int, db: Session) -> str:
    """
    Генерирует календарь в формате .ics для указанного пользователя.
    """
    schedule_items = await get_schedule_list(db=db, limit=1000)

    cal = Calendar()
    for item in schedule_items:
        event = Event()
        event.name = item.get('title', 'Без названия')
        event.begin = item['start_time']
        event.end = item['end_time']
        event.location = item.get('auditorium_name', 'Аудитория не указана')
        
        description = f"Курс: {item.get('course_name', 'Не указан')}\n"
        description += f"Преподаватель: {item.get('teacher_name', 'Не указан')}"
        event.description = description
        
        cal.events.add(event)

    return cal.serialize()
