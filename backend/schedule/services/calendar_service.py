from ics import Calendar, Event
from datetime import datetime
from schedule.api.schedule_api import get_schedule_list

async def generate_calendar_for_user(user_id: int) -> str:
    """
    Генерирует календарь в формате .ics для указанного пользователя.
    """
    # В этой версии мы получаем все события, но в будущем здесь нужно будет
    # реализовать логику получения расписания для конкретного пользователя.
    schedule_items = await get_schedule_list(limit=1000)  # Увеличим лимит для примера

    cal = Calendar()
    for item in schedule_items:
        event = Event()
        # Используем 'title' из слота, так как это название конкретного занятия
        event.name = item.get('title', 'Без названия')
        event.begin = datetime.fromisoformat(item['start_time'])
        event.end = datetime.fromisoformat(item['end_time'])
        event.location = item.get('auditorium_name', 'Аудитория не указана')
        
        # Добавляем больше деталей в описание
        description = f"Курс: {item.get('course_name', 'Не указан')}\n"
        description += f"Преподаватель: {item.get('teacher_name', 'Не указан')}"
        event.description = description
        
        cal.events.add(event)

    # Используем serialize() для явного преобразования в строку, как рекомендуется в ics>=0.8
    return cal.serialize()
