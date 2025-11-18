from pydantic import BaseModel, EmailStr
from typing import Optional


class UserBase(BaseModel):
    full_name: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int
    role: str
    is_active: bool

    model_config = {"from_attributes": True}
