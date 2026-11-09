import pytest
from unittest.mock import AsyncMock
from services.websocket_manager import ConnectionManager
from main import is_allowed_websocket_origin


@pytest.mark.parametrize(
    ("origin", "host", "proto", "expected"),
    [
        ("http://localhost:3000", "localhost:3000", "http", True),
        ("https://localhost:3000", "localhost:3000", "http", False),
        ("https://evil.example", "localhost:3000", "https", False),
        (None, "localhost:3000", "http", False),
        ("null", "localhost:3000", "http", False),
    ],
)
def test_websocket_origin_validation(origin, host, proto, expected):
    assert is_allowed_websocket_origin(origin, host, proto) is expected

@pytest.mark.asyncio
async def test_websocket_manager_logic():
    manager = ConnectionManager()
    mock_ws = AsyncMock()
    
    # Connect
    await manager.connect(mock_ws)
    assert len(manager.active_connections) == 1
    
    # Broadcast
    await manager.broadcast("test message")
    assert mock_ws.send_text.called
    
    # Disconnect
    manager.disconnect(mock_ws)
    assert len(manager.active_connections) == 0


@pytest.mark.asyncio
async def test_broadcast_removes_failed_connections_and_disconnect_is_idempotent():
    manager = ConnectionManager()
    failed_ws = AsyncMock()
    failed_ws.send_text.side_effect = RuntimeError("connection closed")
    manager.active_connections.append(failed_ws)

    await manager.broadcast("event")
    manager.disconnect(failed_ws)

    assert manager.active_connections == []


@pytest.mark.asyncio
async def test_websocket_requires_cookie_authentication():
    from fastapi import HTTPException
    from dependencies import authenticate_websocket

    websocket = AsyncMock()
    websocket.cookies = {}
    websocket.headers = {"authorization": "Bearer ignored"}
    websocket.query_params = {"access_token": "ignored"}

    with pytest.raises(HTTPException) as error:
        await authenticate_websocket(websocket)

    assert error.value.status_code == 401

@pytest.mark.asyncio
async def test_notify_participants_flow():
    from services.notifications import notify_participants_telegram_async
    # Тест логики с пустыми участниками
    result = await notify_participants_telegram_async([], {})
    assert result["success_count"] == 0
