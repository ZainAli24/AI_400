import os
from fastapi import FastAPI, Depends
from sqlmodel import SQLModel, Field, create_engine, Session, select
from dotenv import load_dotenv


load_dotenv()


app = FastAPI(title="Task API", description="Manage Your Tasks")


class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    description: str | None = Field(default=None)


engine = create_engine(url=os.getenv("DATABASE_URL"), echo=True)


class CreatTask(SQLModel):
    title: str
    description: str | None = Field(default=None)



class TaskResponse(SQLModel):
    id: int
    title: str
    description: str | None = Field(default=None)



# 1. How to create table in Database:

# def create_table():
#     print("\n Creating Table....")
#     SQLModel.metadata.create_all(engine)
#     print("\n Table Created Successfully!")


# create_table()

# ----------------------------



# 2. How to actually interact with table:
def get_session():
    with Session(engine) as session:
        yield session



@app.post("/create", response_model=TaskResponse)
def create_task(tasker: CreatTask, session: Session = Depends(get_session)):
    task = Task.model_validate(tasker)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task



@app.get("/tasks", response_model=list[TaskResponse])
def get_tasks(session: Session = Depends(get_session)):
    tasks = session.exec(select(Task)).all()
    return tasks


@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task_by_id(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    return task