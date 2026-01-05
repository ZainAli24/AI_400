# Database Integration Guide

## Table of Contents
- SQLAlchemy (PostgreSQL, MySQL, SQLite)
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
