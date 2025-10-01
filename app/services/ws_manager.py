
from typing import Dict, Set
from fastapi import WebSocket
import json

class WSManager:
    def __init__(self):
        self.rooms: Dict[str, Set[WebSocket]] = {}

    async def connect(self, room: str, ws: WebSocket):
        await ws.accept()
        self.rooms.setdefault(room, set()).add(ws)

    def disconnect(self, room: str, ws: WebSocket):
        if room in self.rooms and ws in self.rooms[room]:
            self.rooms[room].remove(ws)
            if not self.rooms[room]:
                del self.rooms[room]

    async def broadcast(self, room: str, message: dict):
        dead = []
        for ws in list(self.rooms.get(room, [])):
            try:
                await ws.send_text(json.dumps(message))
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(room, ws)

manager = WSManager()
