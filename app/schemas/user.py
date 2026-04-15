from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, ConfigDict, constr


# Reusable constrained types for registration validation.
NameStr = constr(max_length=20)
PasswordStr = constr(min_length=8)


class UserBase(BaseModel):
    name: NameStr = Field(..., json_schema_extra={"example": "Alice Example"})
    email: EmailStr = Field(..., json_schema_extra={"example": "alice@example.com"})


class UserCreate(UserBase):
    password: PasswordStr = Field(..., json_schema_extra={"example": "SuperSecret123"})


class UserLogin(BaseModel):
    email: EmailStr = Field(..., json_schema_extra={"example": "alice@example.com"})
    password: PasswordStr = Field(..., json_schema_extra={"example": "SuperSecret123"})


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginResponse(BaseModel):
    message: str
    user_id: UUID
    token: TokenResponse


class UserResponse(UserBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
