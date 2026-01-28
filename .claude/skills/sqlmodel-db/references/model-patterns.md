# Model Patterns

This guide covers common patterns for designing SQLModel models in FastAPI applications.

## The Base Model Pattern

Separate concerns by creating multiple related classes:

```python
from sqlmodel import SQLModel, Field
from datetime import datetime

# 1. Base model - shared fields, NOT a table
class TaskBase(SQLModel):
    title: str
    description: str | None = None
    completed: bool = False

# 2. Table model - actual database table
class Task(TaskBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

# 3. Create model - fields needed for creation
class TaskCreate(TaskBase):
    pass  # Inherits all from TaskBase

# 4. Update model - all fields optional
class TaskUpdate(SQLModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None

# 5. Public/Response model - what API returns
class TaskPublic(TaskBase):
    id: int
    created_at: datetime
```

### Why This Pattern?

| Model | Purpose | Use Case |
|-------|---------|----------|
| `TaskBase` | Shared validation rules | Reuse across models |
| `Task` | Database table | Store in DB, has ID |
| `TaskCreate` | Request body | POST /tasks |
| `TaskUpdate` | Partial update | PATCH /tasks/{id} |
| `TaskPublic` | Response | Return to client |

### Usage in Endpoints

```python
@app.post("/tasks", response_model=TaskPublic)
def create_task(task: TaskCreate, session: Session = Depends(get_session)):
    db_task = Task.model_validate(task)  # TaskCreate -> Task
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task  # Automatically converted to TaskPublic

@app.patch("/tasks/{task_id}", response_model=TaskPublic)
def update_task(task_id: int, task: TaskUpdate, session: Session = Depends(get_session)):
    db_task = session.get(Task, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Only update provided fields
    update_data = task.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_task, key, value)

    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task
```

## Field Types Reference

### String Fields

```python
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    # Required string
    username: str

    # Optional string
    bio: str | None = None

    # String with constraints
    email: str = Field(unique=True, index=True)

    # String with max length
    display_name: str = Field(max_length=100)
```

### Numeric Fields

```python
class Product(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    # Required integer
    quantity: int

    # Optional integer
    discount_percent: int | None = None

    # Integer with validation
    age: int = Field(ge=0, le=150)  # 0-150

    # Float/decimal
    price: float

    # Float with validation
    rating: float = Field(ge=0.0, le=5.0)
```

### Boolean Fields

```python
class Article(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str

    # Boolean with default
    is_published: bool = False

    # Using Field for explicit default
    is_featured: bool = Field(default=False)
```

### DateTime Fields

```python
from datetime import datetime

class Post(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str

    # Auto-set on creation
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Optional datetime
    published_at: datetime | None = None

    # Updated on each save (handle in code)
    updated_at: datetime | None = None
```

### Enum Fields

```python
from enum import Enum

class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"

class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    status: TaskStatus = TaskStatus.TODO
```

## Table Naming

By default, SQLModel uses the lowercase class name as the table name:

```python
class User(SQLModel, table=True):  # Table name: "user"
    ...

class TaskItem(SQLModel, table=True):  # Table name: "taskitem"
    ...
```

To customize the table name:

```python
class User(SQLModel, table=True):
    __tablename__ = "users"  # Custom table name

    id: int | None = Field(default=None, primary_key=True)
    username: str
```

## Index and Unique Constraints

### Single Column Index

```python
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(index=True)  # Faster lookups by email
```

### Unique Constraint

```python
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True)  # No duplicate emails
```

### Combined Index + Unique

```python
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)  # Unique AND fast lookup
```

## Composite/Compound Keys

For tables with multiple columns forming the primary key:

```python
from sqlalchemy import UniqueConstraint

class UserRole(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("user_id", "role_id"),
    )

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    role_id: int = Field(foreign_key="role.id")
```

## Default Values

### Static Default

```python
class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    priority: int = 0  # Default: 0
    is_active: bool = True  # Default: True
```

### Dynamic Default (Factory)

```python
from datetime import datetime
import uuid

class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    # Current timestamp when created
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Generate UUID
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()))
```

## Validation Rules

SQLModel inherits Pydantic validation:

```python
from pydantic import EmailStr, HttpUrl

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    # Email validation
    email: EmailStr

    # URL validation
    website: HttpUrl | None = None

    # Length validation
    username: str = Field(min_length=3, max_length=50)

    # Numeric range
    age: int = Field(ge=13, le=120)  # 13-120

    # Pattern/Regex
    phone: str = Field(pattern=r"^\+?[0-9]{10,14}$")
```

## Sensitive Fields (Exclude from Response)

```python
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str
    password_hash: str = Field(exclude=True)  # Not in JSON response

class UserPublic(SQLModel):
    """Response model without sensitive fields"""
    id: int
    username: str
    # password_hash not included
```

## Model Configuration

```python
class User(SQLModel, table=True):
    model_config = {
        "strict": True,  # Strict type checking
        "extra": "forbid",  # Don't allow extra fields
    }

    id: int | None = Field(default=None, primary_key=True)
    username: str
```

## Complete Example: Blog System

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from enum import Enum

class PostStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

# --- Author Models ---
class AuthorBase(SQLModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(unique=True)
    bio: str | None = None

class Author(AuthorBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    posts: list["Post"] = Relationship(back_populates="author")

class AuthorCreate(AuthorBase):
    pass

class AuthorPublic(AuthorBase):
    id: int

# --- Post Models ---
class PostBase(SQLModel):
    title: str = Field(min_length=1, max_length=200)
    content: str
    status: PostStatus = PostStatus.DRAFT

class Post(PostBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    author_id: int = Field(foreign_key="author.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    published_at: datetime | None = None

    author: Author = Relationship(back_populates="posts")

class PostCreate(PostBase):
    author_id: int

class PostUpdate(SQLModel):
    title: str | None = None
    content: str | None = None
    status: PostStatus | None = None

class PostPublic(PostBase):
    id: int
    author_id: int
    created_at: datetime
    published_at: datetime | None
```

## Next Steps

- **[crud-operations.md](crud-operations.md)** - Implement CRUD with these models
- **[relationships.md](relationships.md)** - Add relationships between models
