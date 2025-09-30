import os
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlmodel import Session, select
from app.models import User
from app.services.db import get_session

SECRET_KEY = os.getenv("JWT_SECRET", "dev-secret-change-me")
ALGO = "HS256"
ACCESS_TOKEN_EXPIRES_MIN = int(os.getenv("ACCESS_TOKEN_EXPIRES_MIN", "60"))

pwd_ctx = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

def hash_password(p: str) -> str:
    return pwd_ctx.hash(p)

def verify_password(p: str, hp: str) -> bool:
    return pwd_ctx.verify(p, hp)

def create_access_token(user_id: int, role: str) -> str:
    payload = {
        "sub": str(user_id),
        "role": role,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRES_MIN),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGO)

def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
) -> User:
    cred_exc = HTTPException(status_code=401, detail="Invalid credentials")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGO])
        uid = int(payload.get("sub", "0"))
    except (JWTError, ValueError):
        raise cred_exc
    user = session.get(User, uid)
    if not user:
        raise cred_exc
    return user

def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    return user