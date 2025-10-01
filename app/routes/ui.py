
from fastapi import APIRouter
from ..schemas import UiEvent
from ..services.ws_manager import manager

router = APIRouter()

@router.post("/push")
async def push_ui(event: UiEvent):
    await manager.broadcast(event.context_id, event.model_dump())
    return {"ok": True}
