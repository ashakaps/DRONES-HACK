import os, logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.routes import db as db_routes
from app.routes import charts   # 👈 добавь эту строку
from app.routes import geo

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("app")

app = FastAPI(title="DroneRadar API", version="0.2.0")

# CORS
origins = os.getenv("CORS_ORIGINS", "").split(",") if os.getenv("CORS_ORIGINS") else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# статика
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# index.html
@app.get("/")
async def serve_frontend():
    index_path = os.path.join("app", "static", "index.html")
    return FileResponse(index_path)

# health
@app.get("/health")
async def health():
    return {"status": "ok"}

# подключаем роутер для графиков
app.include_router(charts.router)   # 👈 и эту строку
app.include_router(db_routes.router)
app.include_router(geo.router)
