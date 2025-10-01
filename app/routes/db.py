from fastapi import APIRouter
from app.services import db

router = APIRouter(prefix="/db", tags=["db"])

@router.get("/ping")
async def db_ping():
    ok, info = await db.ping()
    return {"ok": ok, "info": info}

@router.get("/status")
async def db_status():
    return await db.status()
