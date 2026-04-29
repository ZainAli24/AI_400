from fastapi import FastAPI, Depends
from sqlmodel import SQLModel, Field, create_engine, Session, select   # type: ignore
from dotenv import load_dotenv
import os

load_dotenv()

# create_engine is used to create engine (for this url database) to manage the connection with the database.
engine = create_engine(os.getenv("DATABASE_URL"), echo=True) # echo=True debugging purpose only, it will log all the sql statements executed, logs will be shown on the terminal/console.

app = FastAPI()

# This Class used to create the table structure in the DB and also used as Pydantic model for data validation in request body of create_task API.

class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)  # primary key defines unique identity for each record/row in the table
    title: str
    description: str | None = Field(default= None)



# @app.post("/tasks")
# def create_task(task: Task):
#     return {"message": "All Good task created successfully!", "task_detail": task}


# -----------------------------------------

# 1. How to create tables in the database using SQLModel?
# def create_tables():
#     print("---------------- Creating Tables in the Database -------------------")
#     SQLModel.metadata.create_all(engine) 
#     print("---------------- Tables created successfully! -------------------")


# create_tables()


# 2. How to actually interact with tables in the database?

# Session is used to manage the transactions with the database ( like insert, update, delete, select ).
def get_session():
    with Session(engine) as session:
        yield session



# Create Task in the database
@app.post("/tasks")
def create_task(task: Task , session: Session = Depends(get_session)):
    session.add(task)
    session.commit()
    print("------------------ Task created:", task ,"-------------------")
    session.refresh(task)
    return task


# Get all Tasks from the database
@app.get("/tasks")
def get_tasks(session: Session = Depends(get_session)):
    tasks = session.exec(select(Task)).all()
    return tasks


# Get Task by ID from the database
@app.get("/tasks/{task_id}")
def get_task_by_id(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    return task




# 4️⃣ Tumhara doubt: “file nahi hai toh close kaise hua?”

# -  Session ek object hai, file nahi

# - Lekin Python ke liye context manager protocol implement kiya gaya hai

# - Matlab: __enter__ (open/start) aur __exit__ (cleanup/close) methods

# - with internally session.__enter__() call karta hai start mein

# - aur block khatam hone ke baad session.__exit__() call karta hai → connection close


#💡 Yani ye bilkul same jaise file ko open/close karte hain, bas yahan file nahi, database connection hai


# -----------------------------------------

