from sqlmodel import SQLModel, Field
from datetime import datetime


class UserBase(SQLModel):
    """Base model with shared fields."""
    email: str = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True)
    is_active: bool = True


class User(UserBase, table=True):
    """Database table model."""
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserCreate(UserBase):
    """Schema for creating a user."""
    password: str


class UserUpdate(SQLModel):
    """Schema for updating a user (all fields optional)."""
    email: str | None = None
    username: str | None = None
    is_active: bool | None = None
    password: str | None = None


class UserPublic(UserBase):
    """Schema for public user response (no password)."""
    id: int
    created_at: datetime
