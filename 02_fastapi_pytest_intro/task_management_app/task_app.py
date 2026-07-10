from fastapi import FastAPI, Depends, HTTPException
from pydantic_settings import BaseSettings
from sqlmodel import SQLModel, Field, select, Session, create_engine
from functools import lru_cache
from enum import Enum


class Status(str, Enum):
    completed = "completed"
    pending = "pending"




class Variables(BaseSettings):
    DATABASE_URL: str

    class Config:
        env_file= ".env"


@lru_cache
def get_db_key():
    return Variables()



app = FastAPI()


class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    description: str | None = Field(default=None)
    status: Status = Field(default=Status.pending)



class Task_input(SQLModel):
    title: str
    description: str | None = Field(default=None)
    status: Status = Field(default=Status.pending)

class TaskResponse(SQLModel):
    id: int
    title: str
    description : str | None = Field(default=None)
    status: Status = Field(default=Status.pending)


class TaskUpdate(SQLModel):
    title: str | None = Field(default=None)
    description: str | None = Field(default=None)
    status : Status | None = Field(default=None)


class TaskReplace(SQLModel):
    title: str 
    description: str 
    status : Status 


# Create Engine:
engine = create_engine(url=get_db_key().DATABASE_URL, echo=True)


# create Table:
# def create_table():
#     SQLModel.metadata.create_all(engine)

# create_table()



# using Sesssion to interact with Table:
def get_session():
    with Session(engine) as session:
        yield session



# 1. Create Task:
@app.post("/create", response_model=TaskResponse)
def create_task(user_task: Task_input, session: Session = Depends(get_session)):
    task = Task.model_validate(user_task)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task



# 2. Get All Tasks:
@app.get("/tasks", response_model=list[TaskResponse])
def get_tasks(session: Session = Depends(get_session)):
    tasks = session.exec(select(Task)).all()
    return tasks


# 3. Get one Task by id:
@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task_by_id(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if task:
        return task
    else:
        raise HTTPException(status_code=404, detail=f"Task not found based on this id: {task_id}")



# 4. Update Task by id:
@app.patch("/tasks/update/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, user_task:TaskUpdate, session : Session = Depends(get_session)):
    db_task = session.get(Task, task_id)
    if db_task:
        if user_task.title:
            db_task.title = user_task.title
        if user_task.description:
            db_task.description = user_task.description
        if user_task.status:
            db_task.status = user_task.status        
        session.add(db_task)
        session.commit()
        session.refresh(db_task)
        return db_task
    else:
        raise HTTPException(status_code=404, detail=f"Task not found based on this id: {task_id}")
    


# 5. replace task by id:
@app.put("/tasks/replace/{task_id}", response_model=TaskResponse)
def replace_task_by_id(task_id: int, user_task: TaskReplace, session : Session = Depends(get_session)):
    db_task = session.get(Task, task_id)
    if db_task:
        db_task.title = user_task.title
        db_task.description = user_task.description
        db_task.status = user_task.status
        session.add(db_task)
        session.commit()
        session.refresh(db_task)
        return db_task
    else:
        raise HTTPException(status_code=404, detail="Task not found!")



# Delete task by id:
@app.delete("/tasks/delete/{task_id}")
def delete_task(task_id: int, session: Session = Depends(get_session)):
    db_task = session.get(Task, task_id)
    if db_task:
        session.delete(db_task)
        session.commit()
        return {"message": f"Task with id {task_id} deleted successfully!"}
    else:
        raise HTTPException(status_code=404, detail="Task not found!")
    
