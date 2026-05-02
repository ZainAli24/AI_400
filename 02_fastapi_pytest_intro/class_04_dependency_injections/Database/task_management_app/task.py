from fastapi import FastAPI, Depends, HTTPException, status
from sqlmodel import SQLModel, Field, Session, create_engine, select
from datetime import datetime, timezone
from dotenv import load_dotenv
import os


load_dotenv("../../.env")


app = FastAPI()

class Tasks(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    description: str | None = Field(default=None)
    status: str = Field(default="pending")
    created_at: datetime = Field(default_factory= lambda: datetime.now(timezone.utc))


class Update_task(SQLModel):
    title: str | None = Field(default=None)
    description: str | None = Field(default=None)
    status: str | None = Field(default=None)


class Create_task(SQLModel):
    title: str 
    description: str | None = Field(default=None)
    status: str | None = Field(default="pending")


class TaskResponse(SQLModel):
    id: int
    title: str
    description: str | None
    status: str
    created_at: datetime



# first create connnection with Db using create_engine method:
engine = create_engine(os.getenv("DATABASE_URL"), echo=True)


# create table:
@app.on_event("startup")
def create_table():
    SQLModel.metadata.create_all(engine)


# Session:
def get_session():
    with Session(engine) as session:
        yield session



# Get Tasks:
@app.get("/tasks", status_code=status.HTTP_200_OK, response_model=list[TaskResponse])
def get_all_tasks(session: Session = Depends(get_session)):
    tasks = session.exec(select(Tasks).order_by(Tasks.id)).all()
    if not tasks:
        raise HTTPException(status_code=404, detail="Tasks not found")
    return tasks


# Get tasks by id:
@app.get("/tasks/{task_id}", status_code=status.HTTP_200_OK, response_model=TaskResponse)
def get_task_by_id(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Tasks, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


# Get task by filtering:
@app.post("/tasks/filtered", status_code=status.HTTP_200_OK, response_model=list[TaskResponse])
def get_task_by_filter(get_task: Update_task, session: Session = Depends(get_session)):
    if get_task.title:
        tasks = session.exec(select(Tasks).where(Tasks.title == get_task.title)).all()
        return tasks
    if get_task.description:
        tasks = session.exec(select(Tasks).where(Tasks.description == get_task.description)).all()
        return tasks
    if get_task.status:
        tasks = session.exec(select(Tasks).where(Tasks.status == get_task.status)).all()
        return tasks
    raise HTTPException(status_code=400, detail="Please provide at least one filter criteria")
    

# Create task :
@app.post("/tasks", status_code=status.HTTP_201_CREATED, response_model=TaskResponse)
def create_task(task:Create_task, session: Session = Depends(get_session)):
    db_task = Tasks(title=task.title, description=task.description, status=task.status)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task


# Update task:
@app.patch("/tasks/{task_id}", status_code=status.HTTP_200_OK, response_model=TaskResponse)
def update_task(task_id: int, task: Update_task, session: Session = Depends(get_session)):
    db_task = session.get(Tasks, task_id)
    if not db_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    if task.title:
        db_task.title = task.title
    if task.description:
        db_task.description = task.description
    if task.status:
        db_task.status = task.status
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task


# Delete Task:
@app.delete("/tasks/{task_id}", status_code=status.HTTP_200_OK, response_model=TaskResponse)
def delete_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Tasks, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit()
    return task
