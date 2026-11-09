from typing import List
from fastapi import WebSocket, WebSocketDisconnect
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info("WebSocket connected. Total active connections: %s", len(self.active_connections))

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info("WebSocket disconnected. Total active connections: %s", len(self.active_connections))

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        disconnected_websockets = []
        for connection in tuple(self.active_connections):
            try:
                await connection.send_text(message)
            except Exception:
                logger.warning("Failed to broadcast to a WebSocket client", exc_info=True)
                disconnected_websockets.append(connection)
        
        for ws in disconnected_websockets:
            self.disconnect(ws)
        
        if disconnected_websockets:
            logger.info(f"Removed {len(disconnected_websockets)} disconnected websockets during broadcast.")

manager = ConnectionManager()
