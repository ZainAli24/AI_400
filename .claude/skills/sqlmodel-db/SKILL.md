---
name: sqlmodel-db
description: |
  SQLModel database design and management for FastAPI applications.
  This skill should be used when users ask to create database models,
  setup SQLModel, design schemas, implement CRUD operations, or work
  with PostgreSQL/SQLite databases in FastAPI projects. Triggers on:
  "create SQLModel", "database model", "create table", "CRUD operations",
  "PostgreSQL setup", "SQLite setup", "model relationships", "foreign key".
---

# SQLModel Database Skill

Build database-driven FastAPI applications with SQLModel - the modern ORM that combines SQLAlchemy power with Pydantic validation.

## What This Skill Does

- Create SQLModel models (`table=True`)
- Setup database engine and session management
- Implement complete CRUD operations
- Design model relationships (One-to-Many, Many-to-Many)
- Configure PostgreSQL (Neon cloud) and SQLite (local dev)
- Database migrations guidance

## What This Skill Does NOT Do

- MongoDB/NoSQL databases (use fastapi-pro skill)
- Raw SQLAlchemy without SQLModel
- Database server administration
- Database backup/restore operations

## Before Implementation

Before writing any database code, gather this information:

1. **Check existing models**: Look for existing SQLModel/SQLAlchemy models
2. **Database type**: PostgreSQL (production) or SQLite (local dev)?
3. **Model requirements**: What fields and relationships are needed?
4. **Naming conventions**: Follow existing project patterns

## Quick Reference

### Model Template

```python
from sqlmodel import SQLModel, Field

class TaskBase(SQLModel):
    """Base model with shared fields (not a table)"""
    title: str
    description: str | None = None

class Task(TaskBase, table=True):
    """Database table model"""
    id: int | None = Field(default=None, primary_key=True)

class TaskCreate(TaskBase):
    """Request body for creating tasks"""
    pass

class TaskUpdate(SQLModel):
    """Request body for updating tasks (all optional)"""
    title: str | None = None
    description: str | None = None
```

### Engine Setup

```python
from sqlmodel import create_engine
import os

# PostgreSQL (Neon cloud)
engine = create_engine(os.getenv("DATABASE_URL"), echo=True)

# SQLite (local development)
engine = create_engine(
    "sqlite:///./app.db",
    echo=True,
    connect_args={"check_same_thread": False}
)
```

### Session Management

```python
from sqlmodel import Session

def get_session():
    with Session(engine) as session:
        yield session
```

### CRUD Patterns

```python
from fastapi import Depends, HTTPException
from sqlmodel import Session, select

# Create
@app.post("/tasks")
def create_task(task: TaskCreate, session: Session = Depends(get_session)):
    db_task = Task.model_validate(task)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

# Read All
@app.get("/tasks")
def get_tasks(session: Session = Depends(get_session)):
    return session.exec(select(Task)).all()

# Read One
@app.get("/tasks/{task_id}")
def get_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

# Update
@app.patch("/tasks/{task_id}")
def update_task(task_id: int, task_update: TaskUpdate, session: Session = Depends(get_session)):
    db_task = session.get(Task, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    for key, value in task_update.model_dump(exclude_unset=True).items():
        setattr(db_task, key, value)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

# Delete
@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit()
```

### Relationship Example

```python
from sqlmodel import SQLModel, Field, Relationship

class Team(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    members: list["User"] = Relationship(back_populates="team")

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    team_id: int | None = Field(default=None, foreign_key="team.id")
    team: Team | None = Relationship(back_populates="members")
```

## Workflow

### Step 1: Install Dependencies

```bash
pip install sqlmodel python-dotenv

# For PostgreSQL (Neon cloud)
pip install psycopg2-binary

# For SQLite (no extra driver needed)
```

### Step 2: Create .env File

```env
# PostgreSQL (Neon)
DATABASE_URL=postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/dbname?sslmode=require

# SQLite (local)
DATABASE_URL=sqlite:///./app.db
```

### Step 3: Setup Database Module

Create `app/db/database.py`:

```python
from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Detect database type and configure accordingly
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        echo=True,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(DATABASE_URL, echo=True)

def create_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
```

### Step 4: Create Models

Create `app/models/task.py`:

```python
from sqlmodel import SQLModel, Field

class TaskBase(SQLModel):
    title: str
    description: str | None = None
    completed: bool = False

class Task(TaskBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

class TaskCreate(TaskBase):
    pass

class TaskUpdate(SQLModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None
```

### Step 5: Create API Endpoints

Create `app/api/tasks.py`:

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.db.database import get_session
from app.models.task import Task, TaskCreate, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("", response_model=Task, status_code=201)
def create_task(task: TaskCreate, session: Session = Depends(get_session)):
    db_task = Task.model_validate(task)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

@router.get("", response_model=list[Task])
def get_tasks(session: Session = Depends(get_session)):
    return session.exec(select(Task)).all()

@router.get("/{task_id}", response_model=Task)
def get_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.patch("/{task_id}", response_model=Task)
def update_task(task_id: int, task_update: TaskUpdate, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    for key, value in task_update.model_dump(exclude_unset=True).items():
        setattr(task, key, value)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit()
```

### Step 6: Wire Up main.py

```python
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db.database import create_tables
from app.api import tasks

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(tasks.router, prefix="/api/v1")
```

### Step 7: Run and Test

```bash
fastapi dev main.py
# Visit http://localhost:8000/docs
```

## Assets

Copy templates for quick start:

- **Single-file example**: `assets/single-file/main.py` - Complete working app in one file
- **Structured app**: `assets/structured/` - Production-ready project structure
- **Environment template**: `assets/.env.example`

## Reference Documentation

Detailed guides for specific topics:

- **[core-concepts.md](references/core-concepts.md)** - SQLModel fundamentals, how it works
- **[model-patterns.md](references/model-patterns.md)** - Model design patterns and field types
- **[crud-operations.md](references/crud-operations.md)** - Complete CRUD implementation guide
- **[relationships.md](references/relationships.md)** - One-to-Many, Many-to-Many relationships
- **[best-practices.md](references/best-practices.md)** - Session management, error handling, database configuration

## Common Issues

### "check_same_thread" Error (SQLite)
SQLite requires `check_same_thread=False` in connect_args for FastAPI.

### PostgreSQL Connection Failed
- Verify DATABASE_URL format
- Check if `psycopg2-binary` is installed
- For Neon: ensure `?sslmode=require` is in URL

### "Table already exists" Error
Tables are created via `SQLModel.metadata.create_all()`. This is idempotent - safe to call multiple times.

### Model Not Creating Table
Ensure `table=True` is set: `class Task(SQLModel, table=True)`
