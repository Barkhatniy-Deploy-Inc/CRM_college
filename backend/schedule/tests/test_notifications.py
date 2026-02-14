import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from services.notifications import send_telegram_message_async, format_slot_telegram_message

@pytest.mark.asyncio
async def test_send_telegram_message_async():
    """Тест асинхронной отправки сообщения"""
    with patch("services.notifications.get_telegram_bot") as mock_get_bot:
        mock_bot = AsyncMock()
        mock_get_bot.return_value = mock_bot
        
        result = await send_telegram_message_async("123456", "Hello World")
        assert result is True
        assert mock_bot.send_message.called

def test_format_slot_telegram_message():
    """Тест форматирования сообщения"""
    slot_data = {
        "course_name": "Python",
        "start_time": "10:00",
        "end_time": "11:30",
        "location": "Room 101",
        "status": "scheduled"
    }
    message = format_slot_telegram_message(slot_data)
    assert "Python" in message
    assert "10:00" in message
    assert "Room 101" in message
