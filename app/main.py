
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import health, ui, ws

app = FastAPI(title="DroneRadar API", version="0.1.0")

# CORS
origins = os.getenv("CORS_ORIGINS", "").split(",") if os.getenv("CORS_ORIGINS") else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(ui.router, prefix="/ui", tags=["ui"])
app.include_router(ws.router, tags=["ws"])
