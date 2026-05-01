from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import SQLModel, Field, create_engine, Session, select
from dotenv import load_dotenv
import os

load_dotenv("../../.env")

app = FastAPI()

# Tasks Table Class:
class Tasks(SQLModel, table=True):
    id: int| None = Field(default=None, primary_key=True)
    title: str
    description: str | None = Field(default=None)
    


# how to connect with database:
engine = create_engine(os.getenv("DATABASE_URL"), echo=True)


# how to create table in database:  we create table in database one time.
# def create_table():
#     print("------------------ Creating Table in Database ------------------")
#     SQLModel.metadata.create_all(engine)
#     print("------------------ Table created successfully! ------------------")


# create_table()



# how to actually interact with tables to perform operation in tables: for this we need Session
def get_session():
    with Session(engine) as session:
        yield session



# get tasks from database tabel:
@app.get("/tasks")
def get_tasks(session: Session = Depends(get_session)):
    tasks = session.exec(select(Tasks)).all()
    return tasks

@app.post("/tasks")
def create_task(task: Tasks, session: Session = Depends(get_session)):
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@app.get("/tasks/{task_id}")
def get_task_by_id(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Tasks, task_id)
    print("------------------ Task found: ", task)
    if not task:  # this means if task is None then we will raise an exception
        raise HTTPException(status_code=404, detail="Task not found")
    return task

