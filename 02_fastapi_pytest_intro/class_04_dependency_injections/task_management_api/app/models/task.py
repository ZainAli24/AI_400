from datetime import datetime, timezone
from sqlmodel import SQLModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class TaskBase(SQLModel):
    title: str
    description: str | None = None
    completed: bool = False
    priority: str | None = None  # "low", "medium", "high"
    due_date: datetime | None = None


class Task(TaskBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=utc_now)


class TaskCreate(TaskBase):
    pass


class TaskUpdate(SQLModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None
    priority: str | None = None
    due_date: datetime | None = None


class TaskResponse(TaskBase):
    id: int
    created_at: datetime
