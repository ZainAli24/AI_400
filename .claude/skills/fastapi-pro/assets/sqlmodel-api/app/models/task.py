from sqlmodel import SQLModel, Field
from datetime import datetime


class TaskBase(SQLModel):
    """Base model with shared fields."""
    title: str
    description: str | None = None
    completed: bool = False


class Task(TaskBase, table=True):
    """Database table model.

    SQLModel combines SQLAlchemy (database) + Pydantic (validation)
    in a single class. The 'table=True' parameter creates the DB table.
    """
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TaskCreate(TaskBase):
    """Schema for creating a task (request body)."""
    pass


class TaskUpdate(SQLModel):
    """Schema for updating a task (all fields optional)."""
    title: str | None = None
    description: str | None = None
    completed: bool | None = None
