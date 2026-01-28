# CRUD Operations Guide

Complete guide to Create, Read, Update, Delete operations with SQLModel.

## Session Basics

Every database operation needs a session:

```python
from sqlmodel import Session, select
from app.db.database import engine

# Direct usage
with Session(engine) as session:
    session.add(task)
    session.commit()
    session.refresh(task)

# FastAPI dependency (recommended)
def get_session():
    with Session(engine) as session:
        yield session

@app.get("/tasks")
def get_tasks(session: Session = Depends(get_session)):
    return session.exec(select(Task)).all()
```

## Create Operations

### Create Single Record

```python
from fastapi import Depends, HTTPException
from sqlmodel import Session

@app.post("/tasks", response_model=Task, status_code=201)
def create_task(task: TaskCreate, session: Session = Depends(get_session)):
    # Convert TaskCreate to Task (table model)
    db_task = Task.model_validate(task)

    session.add(db_task)       # Add to session
    session.commit()           # Save to database
    session.refresh(db_task)   # Get auto-generated fields (id, created_at)

    return db_task
```

### Create with Additional Fields

```python
@app.post("/tasks", response_model=Task)
def create_task(task: TaskCreate, session: Session = Depends(get_session)):
    db_task = Task(
        **task.model_dump(),
        created_at=datetime.utcnow(),
        created_by="system"
    )
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task
```

### Create with Duplicate Check

```python
@app.post("/users", response_model=User)
def create_user(user: UserCreate, session: Session = Depends(get_session)):
    # Check if email exists
    existing = session.exec(
        select(User).where(User.email == user.email)
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = User.model_validate(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user
```

### Create Multiple Records (Bulk)

```python
@app.post("/tasks/bulk", response_model=list[Task])
def create_tasks(tasks: list[TaskCreate], session: Session = Depends(get_session)):
    db_tasks = [Task.model_validate(t) for t in tasks]

    session.add_all(db_tasks)  # Add all at once
    session.commit()

    # Refresh each to get IDs
    for task in db_tasks:
        session.refresh(task)

    return db_tasks
```

## Read Operations

### Get by ID

```python
@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)  # Direct lookup by primary key

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task
```

### Get All

```python
@app.get("/tasks", response_model=list[Task])
def get_tasks(session: Session = Depends(get_session)):
    tasks = session.exec(select(Task)).all()
    return tasks
```

### Get with Pagination

```python
@app.get("/tasks", response_model=list[Task])
def get_tasks(
    skip: int = 0,
    limit: int = 10,
    session: Session = Depends(get_session)
):
    tasks = session.exec(
        select(Task).offset(skip).limit(limit)
    ).all()
    return tasks
```

### Get with Sorting

```python
from sqlmodel import select

@app.get("/tasks", response_model=list[Task])
def get_tasks(session: Session = Depends(get_session)):
    # Ascending
    tasks = session.exec(
        select(Task).order_by(Task.created_at)
    ).all()

    # Descending
    tasks = session.exec(
        select(Task).order_by(Task.created_at.desc())
    ).all()

    return tasks
```

### Get with Filtering

```python
@app.get("/tasks", response_model=list[Task])
def get_tasks(
    completed: bool | None = None,
    session: Session = Depends(get_session)
):
    query = select(Task)

    if completed is not None:
        query = query.where(Task.completed == completed)

    tasks = session.exec(query).all()
    return tasks
```

### Get with Multiple Filters

```python
@app.get("/tasks", response_model=list[Task])
def get_tasks(
    completed: bool | None = None,
    priority: int | None = None,
    search: str | None = None,
    session: Session = Depends(get_session)
):
    query = select(Task)

    if completed is not None:
        query = query.where(Task.completed == completed)

    if priority is not None:
        query = query.where(Task.priority == priority)

    if search:
        query = query.where(Task.title.contains(search))

    return session.exec(query).all()
```

### Get First Match

```python
def get_user_by_email(email: str, session: Session):
    user = session.exec(
        select(User).where(User.email == email)
    ).first()  # Returns None if not found
    return user
```

### Get One (Exactly One Result Expected)

```python
def get_user_by_email(email: str, session: Session):
    user = session.exec(
        select(User).where(User.email == email)
    ).one()  # Raises error if not exactly one result
    return user
```

### Get Count

```python
from sqlmodel import func

@app.get("/tasks/count")
def get_task_count(session: Session = Depends(get_session)):
    count = session.exec(
        select(func.count()).select_from(Task)
    ).one()
    return {"count": count}
```

## Update Operations

### Update (Full Replace)

```python
@app.put("/tasks/{task_id}", response_model=Task)
def update_task(
    task_id: int,
    task: TaskUpdate,
    session: Session = Depends(get_session)
):
    db_task = session.get(Task, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update all fields from request
    task_data = task.model_dump()
    for key, value in task_data.items():
        setattr(db_task, key, value)

    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task
```

### Partial Update (PATCH)

```python
@app.patch("/tasks/{task_id}", response_model=Task)
def update_task(
    task_id: int,
    task: TaskUpdate,
    session: Session = Depends(get_session)
):
    db_task = session.get(Task, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Only update provided fields (exclude_unset=True)
    task_data = task.model_dump(exclude_unset=True)
    for key, value in task_data.items():
        setattr(db_task, key, value)

    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task
```

### Update Specific Field

```python
@app.patch("/tasks/{task_id}/complete", response_model=Task)
def complete_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.completed = True
    task.completed_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)
    return task
```

### Bulk Update

```python
@app.patch("/tasks/complete-all")
def complete_all_tasks(session: Session = Depends(get_session)):
    tasks = session.exec(
        select(Task).where(Task.completed == False)
    ).all()

    for task in tasks:
        task.completed = True

    session.add_all(tasks)
    session.commit()

    return {"updated": len(tasks)}
```

## Delete Operations

### Delete by ID

```python
@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    session.delete(task)
    session.commit()
```

### Delete with Return

```python
@app.delete("/tasks/{task_id}", response_model=Task)
def delete_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    session.delete(task)
    session.commit()

    return task  # Return deleted task
```

### Soft Delete

```python
@app.delete("/tasks/{task_id}")
def soft_delete_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.deleted_at = datetime.utcnow()
    task.is_deleted = True

    session.add(task)
    session.commit()

    return {"message": "Task soft deleted"}
```

### Bulk Delete

```python
@app.delete("/tasks/completed")
def delete_completed_tasks(session: Session = Depends(get_session)):
    tasks = session.exec(
        select(Task).where(Task.completed == True)
    ).all()

    for task in tasks:
        session.delete(task)

    session.commit()

    return {"deleted": len(tasks)}
```

## Advanced Queries

### OR Conditions

```python
from sqlmodel import or_

tasks = session.exec(
    select(Task).where(
        or_(Task.priority == 1, Task.is_urgent == True)
    )
).all()
```

### AND Conditions

```python
from sqlmodel import and_

tasks = session.exec(
    select(Task).where(
        and_(Task.completed == False, Task.priority >= 2)
    )
).all()

# Or simply chain .where()
tasks = session.exec(
    select(Task)
    .where(Task.completed == False)
    .where(Task.priority >= 2)
).all()
```

### IN Clause

```python
task_ids = [1, 2, 3, 4, 5]
tasks = session.exec(
    select(Task).where(Task.id.in_(task_ids))
).all()
```

### LIKE / Contains

```python
# Contains (LIKE %search%)
tasks = session.exec(
    select(Task).where(Task.title.contains("urgent"))
).all()

# Starts with (LIKE search%)
tasks = session.exec(
    select(Task).where(Task.title.startswith("Project"))
).all()

# Case-insensitive
tasks = session.exec(
    select(Task).where(Task.title.ilike("%urgent%"))
).all()
```

### IS NULL / IS NOT NULL

```python
# Tasks without description
tasks = session.exec(
    select(Task).where(Task.description == None)
).all()

# Tasks with description
tasks = session.exec(
    select(Task).where(Task.description != None)
).all()
```

### Aggregate Functions

```python
from sqlmodel import func

# Count
count = session.exec(select(func.count()).select_from(Task)).one()

# Sum
total = session.exec(select(func.sum(Task.priority))).one()

# Average
avg = session.exec(select(func.avg(Task.priority))).one()

# Max/Min
max_priority = session.exec(select(func.max(Task.priority))).one()
```

## Error Handling Pattern

```python
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

@app.post("/users", response_model=User)
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
            detail="User with this email already exists"
        )
```

## Transaction Pattern

```python
def transfer_task(task_id: int, new_project_id: int, session: Session):
    try:
        # Get task
        task = session.get(Task, task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        # Get new project
        project = session.get(Project, new_project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Update task
        task.project_id = new_project_id
        task.transferred_at = datetime.utcnow()

        session.add(task)
        session.commit()
        session.refresh(task)

        return task
    except Exception:
        session.rollback()
        raise
```

## Next Steps

- **[relationships.md](relationships.md)** - Work with related models
- **[best-practices.md](best-practices.md)** - Production patterns
