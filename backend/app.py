from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from typing import List
from datetime import datetime

from db import init_db, get_session, engine
from models import User, RoleEnum
from schemas import UserCreate, UserRead, UserUpdate, LoginRequest, TokenResponse, MeResponse
from auth import hash_password, verify_password, create_access_token, get_current_user, require_admin

app = FastAPI(title="RBAC Demo")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_start():
    init_db()
    from sqlmodel import Session, select
    from models import User
    from auth import hash_password

    admin_email = "admin@example.com"

    # seed admin if missing
    with Session(engine) as s:
        admin_email = "admin@example.com"
        exists = s.exec(select(User).where(User.email == admin_email)).first()
        if not exists:
            s.add(User(email=admin_email, role=RoleEnum.admin, hashed_password=hash_password("admin123")))
            s.commit()

@app.post("/auth/login", response_model=TokenResponse)
def login(req: LoginRequest, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == req.email)).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    user.last_login_at = datetime.utcnow()
    session.add(user)
    session.commit()
    token = create_access_token(user.id, user.role)
    return TokenResponse(access_token=token)

@app.get("/auth/me", response_model=MeResponse)
def me(current: User = Depends(get_current_user)):
    return MeResponse(
        id=current.id, email=current.email, role=current.role,
        created_at=current.created_at, last_login_at=current.last_login_at
    )

# --- Admin users CRUD ---
@app.get("/users", response_model=List[UserRead])
def list_users(_: User = Depends(require_admin), session: Session = Depends(get_session)):
    return session.exec(select(User)).all()

@app.post("/users", response_model=UserRead, status_code=201)
def create_user(data: UserCreate, _: User = Depends(require_admin), session: Session = Depends(get_session)):
    if session.exec(select(User).where(User.email == data.email)).first():
        raise HTTPException(status_code=409, detail="Email already exists")
    u = User(email=data.email, role=data.role, hashed_password=hash_password(data.password))
    session.add(u)
    session.commit()
    session.refresh(u)
    return u

@app.patch("/users/{user_id}", response_model=UserRead)
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

@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int, _: User = Depends(require_admin), session: Session = Depends(get_session)):
    u = session.get(User, user_id)
    if not u:
        raise HTTPException(status_code=404, detail="Not found")
    session.delete(u)
    session.commit()
