# Database Integration Guide

## Table of Contents
- SQLAlchemy (PostgreSQL, MySQL, SQLite)
- SQLModel (Recommended for FastAPI)
- MongoDB with Motor
- Prisma
- Database Best Practices

## SQLAlchemy (Relational Databases)

### Setup

```python
# app/db/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://user:password@localhost/dbname"
# or "mysql://user:password@localhost/dbname"
# or "sqlite:///./app.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Models

```python
# app/models/user.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.db.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
```

### CRUD Operations

```python
# app/api/users.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User

router = APIRouter()

@router.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    return db.query(User).filter(User.id == user_id).first()

@router.post("/users/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.put("/users/{user_id}")
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    for field, value in user.model_dump(exclude_unset=True).items():
        setattr(db_user, field, value)
    db.commit()
    return db_user

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db.query(User).filter(User.id == user_id).delete()
    db.commit()
```

### Migrations with Alembic

```bash
# Install
pip install alembic

# Initialize
alembic init alembic

# Configure alembic.ini
sqlalchemy.url = postgresql://user:password@localhost/dbname

# Create migration
alembic revision --autogenerate -m "Create users table"

# Run migration
alembic upgrade head
```

## SQLModel (Recommended for FastAPI)

SQLModel is created by the same author as FastAPI (tiangolo). It combines SQLAlchemy and Pydantic, making it the most FastAPI-friendly ORM choice.

### Why SQLModel?

| Feature | SQLAlchemy | SQLModel |
|---------|------------|----------|
| Model + Validation | 2 separate classes | Single class |
| Type hints | `Column(Integer)` | Native Python `int` |
| Syntax | Verbose | Clean & simple |
| FastAPI integration | Manual | Native |
| Boilerplate | More | Less |

### Installation

```bash
pip install sqlmodel
```

### Setup

```python
# app/db/database.py
from sqlmodel import SQLModel, create_engine, Session
from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    echo=True  # Set False in production
)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
```

### Models (Single class for DB + Validation)

```python
# app/models/user.py
from sqlmodel import SQLModel, Field
from datetime import datetime

class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True)
    is_active: bool = True

class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(UserBase):
    password: str

class UserUpdate(SQLModel):
    email: str | None = None
    username: str | None = None
    is_active: bool | None = None
    password: str | None = None

class UserPublic(UserBase):
    id: int
```

### CRUD Operations

```python
# app/api/users.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.db.database import get_session
from app.models.user import User, UserCreate, UserUpdate, UserPublic

router = APIRouter()

@router.get("/users", response_model=list[UserPublic])
def get_users(
    skip: int = 0,
    limit: int = 10,
    session: Session = Depends(get_session)
):
    users = session.exec(select(User).offset(skip).limit(limit)).all()
    return users

@router.get("/users/{user_id}", response_model=UserPublic)
def get_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/users", response_model=UserPublic, status_code=201)
def create_user(user: UserCreate, session: Session = Depends(get_session)):
    # Check if exists
    existing = session.exec(
        select(User).where(User.email == user.email)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=f"hashed_{user.password}"  # Use proper hashing
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@router.put("/users/{user_id}", response_model=UserPublic)
def update_user(
    user_id: int,
    user: UserUpdate,
    session: Session = Depends(get_session)
):
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    user_data = user.model_dump(exclude_unset=True)
    if "password" in user_data:
        user_data["hashed_password"] = f"hashed_{user_data.pop('password')}"

    for key, value in user_data.items():
        setattr(db_user, key, value)

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@router.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
```

### Relationships

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

### Quick Single-File Example

```python
# main.py - Complete working example
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import SQLModel, Field, create_engine, Session, select
from contextlib import asynccontextmanager

# Model
class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    description: str | None = None
    completed: bool = False

# Database
engine = create_engine("sqlite:///./tasks.db", echo=True)

def get_session():
    with Session(engine) as session:
        yield session

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

app = FastAPI(lifespan=lifespan)

# CRUD Endpoints
@app.post("/tasks", response_model=Task)
def create_task(task: Task, session: Session = Depends(get_session)):
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@app.get("/tasks", response_model=list[Task])
def get_tasks(session: Session = Depends(get_session)):
    return session.exec(select(Task)).all()

@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.patch("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, completed: bool, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.completed = completed
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit()
```

### SQLModel vs SQLAlchemy - When to Use

| Use Case | Recommendation |
|----------|----------------|
| New FastAPI project | SQLModel |
| Existing SQLAlchemy codebase | Keep SQLAlchemy |
| Complex queries/joins | SQLAlchemy (more mature) |
| Simple CRUD apps | SQLModel |
| Learning FastAPI | SQLModel |
| Need latest SQLAlchemy features | SQLAlchemy |

## MongoDB with Motor

### Setup

```python
# app/db/mongodb.py
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

client = AsyncIOMotorClient(settings.MONGODB_URL)
database = client.get_database(settings.DATABASE_NAME)

async def get_database():
    return database
```

### Async CRUD Operations

```python
# app/api/users.py
from fastapi import APIRouter, Depends
from app.db.mongodb import get_database

router = APIRouter()

@router.get("/users/{user_id}")
async def get_user(user_id: str, db = Depends(get_database)):
    user = await db.users.find_one({"_id": user_id})
    return user

@router.post("/users/")
async def create_user(user: UserCreate, db = Depends(get_database)):
    result = await db.users.insert_one(user.model_dump())
    return {"id": str(result.inserted_id)}

@router.put("/users/{user_id}")
async def update_user(user_id: str, user: UserUpdate, db = Depends(get_database)):
    await db.users.update_one(
        {"_id": user_id},
        {"$set": user.model_dump(exclude_unset=True)}
    )
    return {"status": "updated"}
```

### Using Beanie ODM

```python
# app/models/user.py
from beanie import Document
from pydantic import EmailStr

class User(Document):
    email: EmailStr
    username: str
    hashed_password: str
    is_active: bool = True

    class Settings:
        name = "users"

# Initialize
from beanie import init_beanie

async def init_db():
    await init_beanie(database=database, document_models=[User])

# CRUD with Beanie
user = await User.find_one(User.email == "test@example.com")
user = User(email="test@example.com", username="test")
await user.insert()
await user.save()
await user.delete()
```

## Prisma

### Setup

```bash
# Install
pip install prisma

# Initialize
prisma init

# Define schema in prisma/schema.prisma
datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

generator client {
  provider = "prisma-client-py"
}

model User {
  id        Int      @id @default(autoincrement())
  email     String   @unique
  username  String   @unique
  password  String
  isActive  Boolean  @default(true)
  createdAt DateTime @default(now())
}

# Generate client
prisma generate

# Run migrations
prisma migrate dev --name init
```

### Usage

```python
# app/db/prisma_client.py
from prisma import Prisma

prisma = Prisma()

async def connect_db():
    await prisma.connect()

async def disconnect_db():
    await prisma.disconnect()

# app/api/users.py
from app.db.prisma_client import prisma

@router.get("/users/{user_id}")
async def get_user(user_id: int):
    return await prisma.user.find_unique(where={"id": user_id})

@router.post("/users/")
async def create_user(user: UserCreate):
    return await prisma.user.create(data=user.model_dump())

@router.put("/users/{user_id}")
async def update_user(user_id: int, user: UserUpdate):
    return await prisma.user.update(
        where={"id": user_id},
        data=user.model_dump(exclude_unset=True)
    )
```

## Best Practices

1. **Use Dependency Injection**: Always use `Depends(get_db)` for database sessions
2. **Connection Pooling**: Configure proper pool size for production
3. **Transactions**: Use transactions for multi-step operations
4. **Indexes**: Add indexes on frequently queried columns
5. **Migrations**: Use Alembic for schema changes
6. **Async**: Use async database drivers for better performance
7. **Connection Management**: Always close connections properly
8. **Error Handling**: Handle database errors gracefully
9. **Query Optimization**: Use `.options(joinedload())` for eager loading
10. **Environment Variables**: Store credentials in `.env` files
