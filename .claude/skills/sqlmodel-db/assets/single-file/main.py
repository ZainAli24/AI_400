"""
SQLModel Single-File Example
A complete FastAPI + SQLModel CRUD app in one file.

Run with: fastapi dev main.py
Docs at: http://localhost:8000/docs
"""

from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import SQLModel, Field, Session, create_engine, select
from contextlib import asynccontextmanager
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# --- Database Setup ---
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tasks.db")

# Configure engine based on database type
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        echo=True,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(DATABASE_URL, echo=True)


def get_session():
    """Dependency that provides a database session"""
    with Session(engine) as session:
        yield session


# --- Models ---
class TaskBase(SQLModel):
    """Base model with shared fields"""
    title: str
    description: str | None = None
    completed: bool = False


class Task(TaskBase, table=True):
    """Database table model"""
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TaskCreate(TaskBase):
    """Request body for creating tasks"""
    pass


class TaskUpdate(SQLModel):
    """Request body for updating tasks (all fields optional)"""
    title: str | None = None
    description: str | None = None
    completed: bool | None = None


# --- App Setup ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create tables on startup"""
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(
    title="Task Manager API",
    description="Simple task management with SQLModel",
    lifespan=lifespan
)


# --- CRUD Endpoints ---
@app.post("/tasks", response_model=Task, status_code=201)
def create_task(task: TaskCreate, session: Session = Depends(get_session)):
    """Create a new task"""
    db_task = Task.model_validate(task)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task


@app.get("/tasks", response_model=list[Task])
def get_tasks(
    skip: int = 0,
    limit: int = 20,
    completed: bool | None = None,
    session: Session = Depends(get_session)
):
    """Get all tasks with optional filtering"""
    query = select(Task)

    if completed is not None:
        query = query.where(Task.completed == completed)

    query = query.offset(skip).limit(limit).order_by(Task.created_at.desc())

    return session.exec(query).all()


@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int, session: Session = Depends(get_session)):
    """Get a single task by ID"""
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.patch("/tasks/{task_id}", response_model=Task)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    session: Session = Depends(get_session)
):
    """Update a task (partial update)"""
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Only update provided fields
    update_data = task_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, session: Session = Depends(get_session)):
    """Delete a task"""
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    session.delete(task)
    session.commit()


# --- Extra Endpoints ---
@app.patch("/tasks/{task_id}/toggle", response_model=Task)
def toggle_task(task_id: int, session: Session = Depends(get_session)):
    """Toggle task completion status"""
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.completed = not task.completed
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
