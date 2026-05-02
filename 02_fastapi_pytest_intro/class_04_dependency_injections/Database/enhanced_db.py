from fastapi import FastAPI, Depends, HTTPException, status
from sqlmodel import SQLModel, Field, create_engine, Session, select
from dotenv import load_dotenv
import os
from datetime import datetime, timezone

load_dotenv("../.env")

app = FastAPI()

# Tasks Table Class: class for database table - table=true
class Tasks(SQLModel, table=True):
    id: int| None = Field(default=None, primary_key=True)
    title: str
    description: str | None = Field(default=None)
    status: str = Field(default="pending")
    created_at: datetime = Field(default_factory = lambda: datetime.now(timezone.utc))
    

# Task class for update body: means class for user input and its validation
class Update_Task_User(SQLModel):
    title: str | None = Field(default=None)
    description: str | None = Field(default=None)
    status: str = Field(default="pending")


# Task class for create body: means class for user input and its validation
class Task_User(SQLModel):
    title: str
    description: str | None = Field(default=None)
    status: str = Field(default="pending")


class TaskResponse(SQLModel):
    id: int
    title: str
    description:str | None 
    status: str
    created_at: datetime


# how to connect with database:
engine = create_engine(os.getenv("DATABASE_URL"), echo=True)


# how to create table in database:  we create table in database one time.
def create_table():
    print("------------------ Creating Table in Database ------------------")
    SQLModel.metadata.create_all(engine)
    print("------------------ Table created successfully! ------------------")


# we can create table in database when our application starts: for this we can use event handler of fastapi:
@app.on_event("startup")
def table_request():
    create_table()



# how to actually interact with tables to perform operation in tables: for this we need Session
def get_session():
    with Session(engine) as session:
        yield session



# get tasks from database tabel:
@app.get("/tasks", status_code=status.HTTP_200_OK, response_model=list[TaskResponse])
def get_tasks(session: Session = Depends(get_session)):
    tasks = session.exec(select(Tasks)).all()
    return tasks


# filtered tasks from database table:
# @app.get("/tasks", status_code=status.HTTP_200_OK, response_model=list[TaskResponse])
# def get_tasks(session: Session = Depends(get_session)):
#     task = session.exec(select(Tasks).where(Tasks.description == "ORM basics")).all()
#     return task


@app.post("/tasks", status_code=status.HTTP_201_CREATED, response_model=TaskResponse)
def create_task(task: Task_User, session: Session = Depends(get_session)):
    db_task = Tasks(title=task.title, description=task.description, status=task.status)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task


@app.get("/tasks/{task_id}", status_code=status.HTTP_200_OK, response_model=TaskResponse)
def get_task_by_id(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Tasks, task_id)
    print("------------------ Task found: ", task)
    if not task:  # this means if task is None then we will raise an exception
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.put("/tasks/{task_id}", status_code=status.HTTP_200_OK, response_model=TaskResponse)
def update_task(task_id: int, task: Update_Task_User, session:Session= Depends(get_session)):
    tasker = session.get(Tasks, task_id)
    if not tasker:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.title: # it means if title is not None then we will update the title of tasker
        tasker.title = task.title
    if task.description: # it means if description is not None then we will update the description of tasker
        tasker.description = task.description
    if task.status: # it means if status is not None then we will update the status of tasker
        tasker.status = task.status
    # how to update the task in database:
    session.add(tasker)
    session.commit()
    session.refresh(tasker)
    return tasker


@app.delete("/tasks/{task_id}", status_code=status.HTTP_200_OK, response_model=TaskResponse)
def delete_task(task_id: int, session:Session=Depends(get_session)):
    deleted_task = session.get(Tasks, task_id)
    if not deleted_task:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(deleted_task)
    session.commit()
    return deleted_task

