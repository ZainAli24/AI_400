# Best Practices

Production-ready patterns for SQLModel with FastAPI.

## Session Management

### Always Use Dependency Injection

```python
from fastapi import Depends
from sqlmodel import Session

def get_session():
    with Session(engine) as session:
        yield session

@app.get("/tasks")
def get_tasks(session: Session = Depends(get_session)):
    # Session automatically closed after request
    return session.exec(select(Task)).all()
```

**Why?**
- Automatic cleanup after each request
- Proper connection pooling
- Consistent pattern across endpoints

### Never Create Sessions in Endpoint Body

```python
# BAD - Don't do this
@app.get("/tasks")
def get_tasks():
    session = Session(engine)  # Manual session
    tasks = session.exec(select(Task)).all()
    session.close()  # Easy to forget
    return tasks

# GOOD - Use dependency injection
@app.get("/tasks")
def get_tasks(session: Session = Depends(get_session)):
    return session.exec(select(Task)).all()
```

## Database Configuration

### PostgreSQL (Neon Cloud)

```python
# .env
DATABASE_URL=postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/dbname?sslmode=require

# database.py
import os
from sqlmodel import create_engine
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(
    os.getenv("DATABASE_URL"),
    echo=True,  # Set False in production
    pool_pre_ping=True,  # Check connection health
    pool_size=5,  # Connection pool size
    max_overflow=10  # Extra connections when pool is full
)
```

**Required package:**
```bash
pip install psycopg2-binary
```

### SQLite (Local Development)

```python
# .env
DATABASE_URL=sqlite:///./app.db

# database.py
engine = create_engine(
    os.getenv("DATABASE_URL"),
    echo=True,
    connect_args={"check_same_thread": False}  # Required for FastAPI
)
```

**Why `check_same_thread=False`?**
SQLite by default only allows access from the thread that created it. FastAPI uses multiple threads, so we need to disable this check.

### Environment-Based Configuration

```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    debug: bool = False

    class Config:
        env_file = ".env"

settings = Settings()

# database.py
from app.core.config import settings

engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)
```

### Switching Between PostgreSQL and SQLite

```python
import os
from sqlmodel import create_engine

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

# Detect database type
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        echo=True,
        connect_args={"check_same_thread": False}
    )
else:
    # PostgreSQL or other
    engine = create_engine(
        DATABASE_URL,
        echo=True,
        pool_pre_ping=True
    )
```

## Error Handling

### Standard HTTP Exceptions

```python
from fastapi import HTTPException

@app.get("/tasks/{task_id}")
def get_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
```

### Handle Database Errors

```python
from sqlalchemy.exc import IntegrityError

@app.post("/users")
def create_user(user: UserCreate, session: Session = Depends(get_session)):
    try:
        db_user = User.model_validate(user)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )
```

### Reusable Error Helper

```python
def get_or_404(session: Session, model, id: int, detail: str = "Not found"):
    """Get a record by ID or raise 404"""
    obj = session.get(model, id)
    if not obj:
        raise HTTPException(status_code=404, detail=detail)
    return obj

# Usage
@app.get("/tasks/{task_id}")
def get_task(task_id: int, session: Session = Depends(get_session)):
    return get_or_404(session, Task, task_id, "Task not found")
```

## Table Creation

### Use Lifespan for Table Creation

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlmodel import SQLModel

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables
    SQLModel.metadata.create_all(engine)
    yield
    # Shutdown: Cleanup (if needed)

app = FastAPI(lifespan=lifespan)
```

### Separate Function for Testing

```python
def create_tables():
    """Create all tables - safe to call multiple times"""
    SQLModel.metadata.create_all(engine)

def drop_tables():
    """Drop all tables - USE WITH CAUTION"""
    SQLModel.metadata.drop_all(engine)
```

## Project Structure

### Recommended Layout

```
project/
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── tasks.py
│   │   └── users.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py
│   ├── db/
│   │   ├── __init__.py
│   │   └── database.py
│   └── models/
│       ├── __init__.py
│       ├── task.py
│       └── user.py
├── tests/
│   ├── conftest.py
│   └── test_tasks.py
├── .env
├── .env.example
├── main.py
└── requirements.txt
```

### Model Organization

```python
# app/models/__init__.py
from app.models.task import Task, TaskCreate, TaskUpdate, TaskPublic
from app.models.user import User, UserCreate, UserUpdate, UserPublic

__all__ = [
    "Task", "TaskCreate", "TaskUpdate", "TaskPublic",
    "User", "UserCreate", "UserUpdate", "UserPublic",
]
```

## Query Optimization

### Select Only Needed Columns

```python
from sqlmodel import select

# Select all columns
tasks = session.exec(select(Task)).all()

# Select specific columns (more efficient)
statement = select(Task.id, Task.title)
results = session.exec(statement).all()
```

### Use Pagination

```python
@app.get("/tasks")
def get_tasks(
    skip: int = 0,
    limit: int = 20,
    session: Session = Depends(get_session)
):
    if limit > 100:
        limit = 100  # Cap maximum

    return session.exec(
        select(Task).offset(skip).limit(limit)
    ).all()
```

### Index Frequently Queried Fields

```python
class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(index=True)  # Indexed for faster search
    status: str = Field(index=True)  # Indexed for filtering
    user_id: int = Field(foreign_key="user.id", index=True)  # Indexed FK
```

### Eager Load Relationships

```python
from sqlalchemy.orm import selectinload

@app.get("/teams/{team_id}")
def get_team(team_id: int, session: Session = Depends(get_session)):
    statement = (
        select(Team)
        .options(selectinload(Team.members))
        .where(Team.id == team_id)
    )
    team = session.exec(statement).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team
```

## Security

### Never Expose Internal IDs in URLs (Optional)

```python
import uuid

class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    public_id: str = Field(default_factory=lambda: str(uuid.uuid4()), unique=True)

# Use public_id in URLs
@app.get("/tasks/{public_id}")
def get_task(public_id: str, session: Session = Depends(get_session)):
    task = session.exec(
        select(Task).where(Task.public_id == public_id)
    ).first()
    ...
```

### Validate Input Lengths

```python
class TaskCreate(SQLModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
```

### Hash Sensitive Data

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True)
    hashed_password: str  # Never store plain passwords

def create_user(user: UserCreate, session: Session):
    db_user = User(
        email=user.email,
        hashed_password=pwd_context.hash(user.password)
    )
    session.add(db_user)
    session.commit()
    return db_user
```

## Testing

### Test Database Setup

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool

from app.db.database import get_session
from main import app

@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",  # In-memory database
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
```

### Test Examples

```python
# tests/test_tasks.py
def test_create_task(client):
    response = client.post("/tasks", json={"title": "Test Task"})
    assert response.status_code == 201
    assert response.json()["title"] == "Test Task"

def test_get_task_not_found(client):
    response = client.get("/tasks/999")
    assert response.status_code == 404
```

## Common Anti-Patterns

### Don't Query in Loops

```python
# BAD - N+1 query problem
tasks = session.exec(select(Task)).all()
for task in tasks:
    print(task.owner.name)  # Separate query for each task!

# GOOD - Eager load
statement = select(Task).options(selectinload(Task.owner))
tasks = session.exec(statement).all()
for task in tasks:
    print(task.owner.name)  # Already loaded
```

### Don't Forget to Commit

```python
# BAD - Changes not saved
session.add(task)
# Missing session.commit()

# GOOD
session.add(task)
session.commit()
session.refresh(task)
```

### Don't Return SQLModel Objects with Sensitive Fields

```python
# BAD - Exposes password hash
@app.get("/users/{user_id}")
def get_user(user_id: int, session: Session = Depends(get_session)):
    return session.get(User, user_id)

# GOOD - Use response model
@app.get("/users/{user_id}", response_model=UserPublic)
def get_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404)
    return user
```

## Environment Files

### .env.example (Template)

```env
# Database
DATABASE_URL=sqlite:///./app.db

# For PostgreSQL (Neon):
# DATABASE_URL=postgresql://user:password@ep-xxx.aws.neon.tech/dbname?sslmode=require

# App Settings
DEBUG=true
SECRET_KEY=change-me-in-production
```

### .gitignore

```gitignore
# Environment
.env
*.env

# Database
*.db
*.sqlite

# Python
__pycache__/
*.py[cod]
.venv/
venv/
```

## Production Checklist

- [ ] Set `echo=False` in `create_engine()`
- [ ] Use environment variables for all secrets
- [ ] Add proper indexes on frequently queried columns
- [ ] Implement pagination for list endpoints
- [ ] Use response models to control what's exposed
- [ ] Add error handling for database operations
- [ ] Set up proper connection pooling for PostgreSQL
- [ ] Never commit `.env` file to git
- [ ] Hash all passwords before storing
- [ ] Validate all input data with Pydantic/SQLModel
