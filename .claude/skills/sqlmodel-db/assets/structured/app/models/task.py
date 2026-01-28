"""
Task model and schemas.
"""

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime


class TaskBase(SQLModel):
    """Base model with shared fields"""
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    completed: bool = False
    priority: int = Field(default=0, ge=0, le=5)


class Task(TaskBase, table=True):
    """Database table model"""
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Foreign key to user (owner)
    owner_id: int | None = Field(default=None, foreign_key="user.id", index=True)

    # Relationship to user
    owner: "User | None" = Relationship(back_populates="tasks")


class TaskCreate(TaskBase):
    """Request body for creating tasks"""
    owner_id: int | None = None


class TaskUpdate(SQLModel):
    """Request body for updating tasks (all fields optional)"""
    title: str | None = None
    description: str | None = None
    completed: bool | None = None
    priority: int | None = Field(default=None, ge=0, le=5)


class TaskPublic(TaskBase):
    """Response model for tasks"""
    id: int
    created_at: datetime
    owner_id: int | None


# Import User at the end to avoid circular imports
from app.models.user import User

Task.model_rebuild()
