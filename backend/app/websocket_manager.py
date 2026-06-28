from fastapi import WebSocket
from typing import Set
import json


class WebSocketManager:
    def __init__(self):
        self.connections: dict[int, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        if user_id not in self.connections:
            self.connections[user_id] = set()
        self.connections[user_id].add(websocket)

    def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.connections:
            self.connections[user_id].discard(websocket)
            if not self.connections[user_id]:
                del self.connections[user_id]

    async def send_notification(self, user_id: int, notification: dict):
        if user_id in self.connections:
            for ws in self.connections[user_id]:
                try:
                    await ws.send_json(notification)
                except Exception:
                    pass

    async def broadcast(self, message: dict):
        for user_connections in self.connections.values():
            for ws in user_connections:
                try:
                    await ws.send_json(message)
                except Exception:
                    pass


ws_manager = WebSocketManager()
