import os, logging
from pathlib import Path
from app.routes import auth
from app.services.db import init_db, engine
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.routes import db as db_routes
from app.routes import charts   # 👈 добавь эту строку
from app.routes import geo

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("app")

FRONTEND_DIST = Path(__file__).resolve().parent / "static"
INDEX_HTML = FRONTEND_DIST / "index.html"

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


# health
@app.get("/health")
async def health():
    return {"status": "ok"}

# подключаем роутер для графиков
app.include_router(charts.router)   # 👈 и эту строку
app.include_router(db_routes.router)
app.include_router(geo.router)

# ui и ws пока не подключаем, если нужны — добавим отдельно

# подключаем роутера для авторизации
app.include_router(auth.router, prefix="/api")


@app.on_event("startup")
def on_start():
    init_db()
    from sqlmodel import Session, select
    from app.models import User, RoleEnum
    from app.routes.auth_funcs import hash_password

    # seed admin if missing
    with Session(engine) as s:
        admin_email = "admin@example.com"
        exists = s.exec(select(User).where(User.email == admin_email)).first()
        if not exists:
            s.add(User(email=admin_email, role=RoleEnum.admin, hashed_password=hash_password("admin123")))
            s.commit()


@app.get("/routes")
def get_routes():
    routes = []
    for route in app.routes:
        routes.append({
            "path": route.path,
            "methods": getattr(route, "methods", None)
        })
    return routes


# статика
app.mount("/oldstatic", StaticFiles(directory="/app/app/oldstatic", html=True), name="frontend")
app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")



@app.middleware("http")
async def spa_fallback(request: Request, call_next):
    resp = await call_next(request)
    p = request.url.path
    # Fallback только для GET HTML и не-API путей
    if (
        resp.status_code == 404
        and request.method == "GET"
        and not p.startswith("/api")
        and not p.startswith("/oldstatic")
        and p not in ("/openapi.json", "/docs", "/redoc")
        and "text/html" in request.headers.get("accept", "")
        and INDEX_HTML.is_file()
    ):
        return FileResponse(INDEX_HTML)
    return resp

