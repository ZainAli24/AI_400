# SQLModel Core Concepts

This guide explains the fundamental concepts of SQLModel for beginners.

## What is SQLModel?

SQLModel is a Python library that combines two powerful tools:

1. **SQLAlchemy** - The most popular Python SQL toolkit (handles database operations)
2. **Pydantic** - Data validation library used by FastAPI (handles data validation)

**Key benefit**: One class does the work of two - defines both database schema AND request validation.

## The Data Flow

When you make an API request, data flows through several layers:

```
Your Python Code
      ↓
   SQLModel (defines models)
      ↓
   Session (manages transactions)
      ↓
   Engine (manages connections)
      ↓
   psycopg2 (database driver)
      ↓
   PostgreSQL Database
```

### Understanding Each Component

#### 1. SQLModel Class
Defines the structure of your data:

```python
from sqlmodel import SQLModel, Field

class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    description: str | None = None
```

#### 2. Engine
Creates and manages database connections:

```python
from sqlmodel import create_engine

engine = create_engine("postgresql://user:pass@localhost/db")
```

The engine is like a "connection factory" - it doesn't connect immediately but creates connections when needed.

#### 3. Session
Manages a single transaction (a group of database operations):

```python
from sqlmodel import Session

with Session(engine) as session:
    session.add(task)      # Add to transaction
    session.commit()       # Save changes
    session.refresh(task)  # Get updated data (like auto-generated ID)
```

#### 4. Database Driver (psycopg2)
The actual Python library that talks to PostgreSQL:

```bash
pip install psycopg2-binary
```

- `psycopg2` - Requires compilation (production)
- `psycopg2-binary` - Pre-compiled (development, easier to install)

## Understanding `table=True`

The `table=True` parameter is crucial:

```python
# NOT a database table - just a Pydantic model for validation
class TaskBase(SQLModel):
    title: str

# IS a database table - creates actual table in database
class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
```

When SQLModel sees `table=True`:
- It tells SQLAlchemy to create a table
- The class name becomes the table name (lowercase: `task`)
- Each field becomes a column

## Primary Keys

Every table needs a primary key - a unique identifier for each row:

```python
class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
```

**Why `int | None` with `default=None`?**
- When creating a new task, you don't provide the ID
- The database auto-generates it (auto-increment)
- After `session.refresh()`, the `id` field will have the generated value

## Type Hints in SQLModel

SQLModel uses Python type hints to define columns:

| Python Type | SQL Type | Notes |
|-------------|----------|-------|
| `str` | VARCHAR | Required string |
| `str \| None` | VARCHAR NULL | Optional string |
| `int` | INTEGER | Required integer |
| `int \| None` | INTEGER NULL | Optional integer |
| `bool` | BOOLEAN | True/False |
| `float` | FLOAT | Decimal numbers |
| `datetime` | TIMESTAMP | Date and time |

## Field Options

The `Field()` function adds constraints:

```python
from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    username: str = Field(max_length=50, index=True)
    age: int | None = Field(default=None, ge=0, le=150)
    is_active: bool = Field(default=True)
```

| Option | Purpose |
|--------|---------|
| `primary_key=True` | Unique identifier for the row |
| `unique=True` | No duplicates allowed |
| `index=True` | Faster searches on this column |
| `default=value` | Default value if not provided |
| `default_factory=func` | Function to generate default |
| `max_length=n` | Maximum string length |
| `ge=n` | Greater than or equal (validation) |
| `le=n` | Less than or equal (validation) |

## Creating Tables

Tables are created from your model definitions:

```python
from sqlmodel import SQLModel, create_engine

engine = create_engine("sqlite:///./app.db")

# Creates all tables defined with table=True
SQLModel.metadata.create_all(engine)
```

**When to call this:**
- At application startup (using lifespan)
- Safe to call multiple times (won't recreate existing tables)

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

app = FastAPI(lifespan=lifespan)
```

## SQLModel vs Pure SQLAlchemy

### SQLAlchemy (Separate Models)
```python
# Database model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)

# Pydantic model for validation
class UserCreate(BaseModel):
    name: str

# Pydantic model for response
class UserResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True
```

### SQLModel (Combined)
```python
# One class does everything
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
```

**Benefits of SQLModel:**
- Less code duplication
- Python-native type hints
- Automatic validation
- Built for FastAPI

## Common Misconceptions

### "Session is like a file"
A Session is not a file - it's a transaction manager. The `with` statement ensures proper cleanup:

```python
with Session(engine) as session:
    # session.__enter__() called - starts transaction
    session.add(task)
    session.commit()
    # session.__exit__() called - closes connection
```

### "I need to install SQLAlchemy separately"
No! SQLModel includes SQLAlchemy:

```bash
pip install sqlmodel  # Includes SQLAlchemy and Pydantic
```

### "create_engine connects to the database"
No, it creates a connection factory. Actual connections happen when you:
- Create a Session
- Execute queries
- Call methods like `session.exec()`

## Next Steps

- **[model-patterns.md](model-patterns.md)** - Learn model design patterns
- **[crud-operations.md](crud-operations.md)** - Implement CRUD operations
- **[relationships.md](relationships.md)** - Add relationships between models
