from datetime import datetime
from typing import Optional
from enum import Enum as PyEnum

from sqlalchemy import Column, Enum as SAEnum, String
from sqlmodel import SQLModel, Field

class RoleEnum(str, PyEnum):
    admin = "admin"
    operator = "operator"

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(sa_column=Column(String, unique=True, index=True, nullable=False))
    role: RoleEnum = Field(
        default=RoleEnum.operator,
        sa_column=Column(SAEnum(RoleEnum, name="role_enum"), nullable=False)
    )
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    last_login_at: Optional[datetime] = None