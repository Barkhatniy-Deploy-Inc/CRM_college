import logging
from typing import List, Dict
import os
from dotenv import load_dotenv
import asyncio
import telegram
from schedule.database.database import get_db

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
NOTIFICATIONS_ENABLED = bool(TELEGRAM_BOT_TOKEN)
_bot_instance = None

def get_telegram_bot():
    global _bot_instance
    if _bot_instance is None:
        if not TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN не установлен в .env")
        _bot_instance = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
    return _bot_instance

async def subscribe_telegram_notification(user_id: int, telegram_id: str) -> dict:
    """Подписка пользователя на Telegram уведомления."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET telegram_id = ? WHERE id = ?", (telegram_id, user_id))
    return {"message": "Telegram подписка активирована", "telegram_id": telegram_id}

def format_slot_telegram_message(slot_data: dict, notification_type: str = "new") -> str:
    """Формирует текстовое сообщение для Telegram об уроке."""
    headers = {
        "new": "🆕 <b>Новый урок добавлен!</b>",
        "status_changed": "🔄 <b>Изменение статуса урока</b>",
        "reminder": "⏰ <b>Напоминание об уроке</b>"
    }
    header = headers.get(notification_type, "📌 <b>Уведомление об уроке</b>")

    status_emoji = {"scheduled": "📅", "in_progress": "▶️", "completed": "✅", "cancelled": "❌"}
    status = slot_data.get('status', 'scheduled')
    status_text = f"{status_emoji.get(status, '📌')} {status}"

    message = f"""{header}

📚 <b>Курс:</b> {slot_data.get('course_name', 'Не указан')}
⏰ <b>Начало:</b> {slot_data.get('start_time', 'Не указано')}
⏱ <b>Конец:</b> {slot_data.get('end_time', 'Не указано')}
📍 <b>Аудитория:</b> {slot_data.get('location', 'Не указано')}
🏷 <b>Статус:</b> {status_text}
"""
    return message

async def notify_participants_telegram_async(participants: List[dict], slot_data: dict, notification_type: str = "new") -> Dict[str, any]:
    """Асинхронная отправка уведомлений в Telegram."""
    if not NOTIFICATIONS_ENABLED or not participants:
        return {"success_count": 0, "failed_count": 0}

    message = format_slot_telegram_message(slot_data, notification_type)
    tasks = [send_telegram_message_async(str(p['telegram_chat_id']), message) for p in participants if p.get('telegram_chat_id')]
    
    if not tasks:
        return {"success_count": 0, "failed_count": 0}

    results = await asyncio.gather(*tasks)
    success_count = sum(1 for r in results if r)
    return {"success_count": success_count, "failed_count": len(results) - success_count}

async def send_telegram_message_async(chat_id: str, message: str) -> bool:
    """Асинхронная отправка одного сообщения в Telegram."""
    try:
        bot = get_telegram_bot()
        await bot.send_message(chat_id=int(chat_id), text=message, parse_mode='HTML')
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка отправки в чат {chat_id}: {e}")
        return False

async def notify_slot_created(participants: List[dict], slot_data: dict) -> Dict[str, any]:
    return await notify_participants_telegram_async(participants, slot_data, "new")

async def notify_slot_status_changed(participants: List[dict], slot_data: dict, old_status: str) -> Dict[str, any]:
    slot_data['old_status'] = old_status
    return await notify_participants_telegram_async(participants, slot_data, "status_changed")
