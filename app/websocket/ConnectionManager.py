from typing import Any
import asyncio

from fastapi import WebSocket
from starlette.websockets import WebSocketState


class ConnectionManager:
    active_connections: dict[Any, list[str]] = {}
    _loop: asyncio.AbstractEventLoop = None

    def set_event_loop(self, loop: asyncio.AbstractEventLoop):
        """Lưu event loop để sử dụng trong sync methods"""
        self._loop = loop

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        if websocket not in self.active_connections:
            self.active_connections[websocket] = []

    async def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            del self.active_connections[websocket]

    async def add_listen_event(self, websocket: WebSocket, event: str):
        if websocket in self.active_connections and event not in self.active_connections[websocket]:
            self.active_connections[websocket].append(event)

    async def remove_listen_event(self, websocket: WebSocket, event: str):
        if websocket in self.active_connections and event in self.active_connections[websocket]:
            self.active_connections[websocket].remove(event)

    async def send_message_json(self, event, message: dict):
        for connection, events in self.active_connections.items():
            if connection.application_state == WebSocketState.CONNECTED:
                if event in events:
                    await connection.send_json({"event": event, "data": message})

    def send_message_json_sync(self, event, message: dict):
        """Sync wrapper để gọi từ thread - fire and forget"""
        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self.send_message_json(event, message), self._loop
            )
        else:
            print("Event loop not available, cannot send message")


connection_websocket_manager = ConnectionManager()
