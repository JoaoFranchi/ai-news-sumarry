from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    name: str = Field(..., example="Alice Example")
    email: EmailStr = Field(..., example="alice@example.com")


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, example="SuperSecret123")


class UserLogin(BaseModel):
    email: EmailStr = Field(..., example="alice@example.com")
    password: str = Field(..., min_length=8, example="SuperSecret123")


class UserResponse(UserBase):
    id: UUID
    created_at: datetime

    class Config:
        orm_mode = True
