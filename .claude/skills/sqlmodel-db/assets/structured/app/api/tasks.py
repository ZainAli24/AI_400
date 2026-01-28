"""
Task API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.db.database import get_session
from app.models.task import Task, TaskCreate, TaskUpdate, TaskPublic

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskPublic, status_code=201)
def create_task(task: TaskCreate, session: Session = Depends(get_session)):
    """Create a new task"""
    db_task = Task.model_validate(task)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task


@router.get("", response_model=list[TaskPublic])
def get_tasks(
    skip: int = 0,
    limit: int = 20,
    completed: bool | None = None,
    owner_id: int | None = None,
    session: Session = Depends(get_session)
):
    """Get all tasks with optional filtering"""
    query = select(Task)

    if completed is not None:
        query = query.where(Task.completed == completed)

    if owner_id is not None:
        query = query.where(Task.owner_id == owner_id)

    query = query.offset(skip).limit(limit).order_by(Task.created_at.desc())

    return session.exec(query).all()


@router.get("/{task_id}", response_model=TaskPublic)
def get_task(task_id: int, session: Session = Depends(get_session)):
    """Get a single task by ID"""
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{task_id}", response_model=TaskPublic)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    session: Session = Depends(get_session)
):
    """Update a task (partial update)"""
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = task_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, session: Session = Depends(get_session)):
    """Delete a task"""
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    session.delete(task)
    session.commit()


@router.patch("/{task_id}/toggle", response_model=TaskPublic)
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
