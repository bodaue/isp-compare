import re
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    fullname: str = Field(..., max_length=256)

    username: str = Field(..., min_length=4, max_length=64)
    password: str = Field(..., min_length=8, examples=["Password123", "Password123!"])

    email: EmailStr

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserLogin(BaseModel):
    username: str
    password: str


class UserProfile(BaseModel):
    id: UUID

    fullname: str
    username: str

    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class UserProfileUpdate(BaseModel):
    fullname: str | None = Field(None, max_length=256)
    username: str | None = Field(None, min_length=4, max_length=64)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"  # noqa: S105
