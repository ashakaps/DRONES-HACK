
from datetime import datetime
from typing import List
from fastapi import APIRouter, FastAPI, Depends, HTTPException
import app
from app.models import User
from app.routes.auth_funcs import create_access_token, get_current_user, hash_password, require_admin, verify_password
from app.services.db import get_session
from app.schemas import UserCreate, UserRead, UserUpdate, LoginRequest, TokenResponse, MeResponse
from sqlmodel import Session, select


router = APIRouter()

@router.get("")
async def health():
    return {"status": "ok"}

@router.post("/auth/login", response_model=TokenResponse)
def login(req: LoginRequest, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == req.email)).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    user.last_login_at = datetime.utcnow()
    session.add(user)
    session.commit()
    token = create_access_token(user.id, user.role)
    return TokenResponse(access_token=token)

@router.get("/auth/me", response_model=MeResponse)
def me(current: User = Depends(get_current_user)):
    return MeResponse(
        id=current.id, email=current.email, role=current.role,
        created_at=current.created_at, last_login_at=current.last_login_at
    )

# --- Admin users CRUD ---
@router.get("/users", response_model=List[UserRead])
def list_users(_: User = Depends(require_admin), session: Session = Depends(get_session)):
    return session.exec(select(User)).all()

@router.post("/users", response_model=UserRead, status_code=201)
def create_user(data: UserCreate, _: User = Depends(require_admin), session: Session = Depends(get_session)):
    if session.exec(select(User).where(User.email == data.email)).first():
        raise HTTPException(status_code=409, detail="Email already exists")
    u = User(email=data.email, role=data.role, hashed_password=hash_password(data.password))
    session.add(u)
    session.commit()
    session.refresh(u)
    return u

@router.patch("/users/{user_id}", response_model=UserRead)
def update_user(user_id: int, data: UserUpdate, _: User = Depends(require_admin), session: Session = Depends(get_session)):
    u = session.get(User, user_id)
    if not u:
        raise HTTPException(status_code=404, detail="Not found")
    if data.role is not None:
        u.role = data.role
    if data.password:
        u.hashed_password = hash_password(data.password)
    session.add(u)
    session.commit()
    session.refresh(u)
    return u

@router.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int, _: User = Depends(require_admin), session: Session = Depends(get_session)):
    u = session.get(User, user_id)
    if not u:
        raise HTTPException(status_code=404, detail="Not found")
    session.delete(u)
    session.commit()

@router.get("/routes")
def get_routes():
    routes = []
    for route in app.routes:
        routes.append({
            "path": route.path,
            "methods": getattr(route, "methods", None)
        })
    return routes