import pytest
import json
from unittest.mock import AsyncMock, MagicMock
from services.websocket_manager import ConnectionManager

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
async def test_notify_participants_flow():
    from services.notifications import notify_participants_telegram_async
    # Тест логики с пустыми участниками
    result = await notify_participants_telegram_async([], {})
    assert result["success_count"] == 0
