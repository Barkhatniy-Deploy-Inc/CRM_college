import pytest
from unittest.mock import AsyncMock, patch
from database.models import User
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


@pytest.mark.asyncio
async def test_subscribe_telegram_accepts_json_body(client, mock_auth, db):
    """Telegram ID передаётся явно в JSON body, не query parameter."""
    user = User(
        full_name="Тестовый пользователь",
        email="telegram@example.test",
        password_hash="hash",
    )
    db.add(user)
    db.commit()

    response = await client.post(
        "/api/schedule/notifications/subscribe-telegram",
        json={"telegram_id": "123456"},
    )

    assert response.status_code == 200
    assert response.json()["telegram_id"] == "123456"
    db.refresh(user)
    assert user.telegram_id == "123456"
