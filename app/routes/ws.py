
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ..services.ws_manager import manager

router = APIRouter()

@router.websocket("/ws/{context_id}")
async def ws_room(ws: WebSocket, context_id: str):
    await manager.connect(context_id, ws)
    try:
        while True:
            # При желании клиент может что-то присылать
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(context_id, ws)
