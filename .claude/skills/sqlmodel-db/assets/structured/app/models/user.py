"""
User model and schemas.
"""

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime


class UserBase(SQLModel):
    """Base model with shared fields"""
    username: str = Field(min_length=3, max_length=50, unique=True, index=True)
    email: str = Field(unique=True, index=True)
    is_active: bool = True


class User(UserBase, table=True):
    """Database table model"""
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # One user has many tasks
    tasks: list["Task"] = Relationship(back_populates="owner")


class UserCreate(UserBase):
    """Request body for creating users"""
    pass


class UserUpdate(SQLModel):
    """Request body for updating users (all fields optional)"""
    username: str | None = None
    email: str | None = None
    is_active: bool | None = None


class UserPublic(UserBase):
    """Response model for users"""
    id: int
    created_at: datetime


class UserWithTasks(UserPublic):
    """Response model for user with their tasks"""
    tasks: list["TaskPublic"] = []


# Import Task at the end to avoid circular imports
from app.models.task import Task, TaskPublic

User.model_rebuild()
UserWithTasks.model_rebuild()
