# schemas.py
from datetime import datetime
from typing import Optional
from enum import Enum as PyEnum
from pydantic import BaseModel, EmailStr

class Role(str, PyEnum):
    admin = "admin"
    operator = "operator"


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: Role = Role.operator


class UserRead(BaseModel):
    id: int
    email: EmailStr
    role: Role
    created_at: datetime
    last_login_at: Optional[datetime]


class UserUpdate(BaseModel):
    role: Optional[Role] = None
    password: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MeResponse(UserRead):
    pass
