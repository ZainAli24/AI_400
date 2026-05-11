from fastapi import FastAPI, Depends, status, HTTPException
from sqlmodel import SQLModel, Session, create_engine, select, Field
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta, timezone
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from jose import jwt, JWTError, ExpiredSignatureError
from typing import Optional, Literal
from fastapi.security import OAuth2PasswordBearer

acccess_token = OAuth2PasswordBearer(tokenUrl="login")


password_hash = PasswordHash((Argon2Hasher(), ))


# Generate a secure random secret key:
# import secrets
# secret_key = secrets.token_hex(32)  # Generates a 64-character hexadecimal string (256 bits)
# print(f"Generated Secret Key: {secret_key}")


load_dotenv(".env")

SECRET_KEY = os.getenv("SECRET_KEY")
ALOGRITHUM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))


app = FastAPI()


# connection with DB:
engine = create_engine(os.getenv("DATABASE_URL"), echo=True)


# Create user table in database:
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str 
    email: str 
    password: str 
    created_at: datetime = Field(default_factory= datetime.now) # no neeed to make it human readable because SQLModel/SQLite automatically store it in human readable format.
    # SQLModel/SQLite automatically readable format mein store karta hai: 2026-05-04 14:30:00



# Create User class:
class UserData(SQLModel):
    name: str 
    email: str 
    password: str 

# login User class:
class loginData(SQLModel):
    email: str
    password: str


#  Task table
class Tasks(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    description: str | None = Field(default=None)
    status: str = Field(default="pending")
    owner_id: int = Field(foreign_key="user.id")
    created_at : datetime = Field(default_factory=datetime.now)


# create task:
class Create_Task(SQLModel):
    title: str
    description: str | None = Field(default=None)
    status: Literal["pending", "in progress", "completed"] = Field(default="pending")


# Task response model:
class Task_Response(SQLModel):
    id: int
    title: str
    description: str | None = Field(default=None)
    status: str 
    created_at : datetime


# Update Task model:
class Update_task(SQLModel):
    title: str | None = Field(default=None)
    description: str | None = Field(default=None)
    status: str | None = Field(default=None)

    

# create table function:
def create_table():
    SQLModel.metadata.create_all(engine)


# create session:
def get_session():
    with Session(engine) as session:
        yield session



@app.on_event("startup")
def create_user_table():
    create_table()


# Password Hashing:
def hash_password(password: str):
    return password_hash.hash(password)

# Password verify:
def verify_password(password: str, hashed_password:str):
    return password_hash.verify(password, hashed_password)


# Create JWT Token:
def create_access_token(user_data: dict, expire_time: Optional[timedelta] = None):
    encode_data = user_data.copy()
    expire = datetime.now(timezone.utc) + (expire_time or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    encode_data.update({"exp": expire})

    token = jwt.encode(encode_data, SECRET_KEY, ALOGRITHUM)
    return {"token_type": "bearer", "access_token": token}


# Verify JWT Token:
def verify_token(token: str) -> Optional[dict]:
    try:
        user_obj = jwt.decode(token, SECRET_KEY, algorithms=[ALOGRITHUM])
        return user_obj
    except ExpiredSignatureError:
        return "expired"
    except JWTError:
        return None
    

# Get_access user:
def get_access_user(token = Depends(acccess_token), session: Session = Depends(get_session)):

    credentailHttpException = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentails",
        headers={"WWW-Authenticate": "Baerer"},
    )


    user_data = verify_token(token)

    if user_data == "expired":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Token has expired! Please login again.",
            headers={"WWW-Authenticate": "Baerer"}
        )

    if not user_data:
        raise credentailHttpException
    
    email = user_data.get("sub")
    if not email:
        raise credentailHttpException
    
    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        raise credentailHttpException
    
    return user




# Create user account:
@app.post("/signin")
def create_user(user:UserData,  session: Session = Depends(get_session)):
    if session.exec(select(User).where(User.email == user.email)).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"You already have an account with this email: {user.email}")
    hash_user_pass = hash_password(user.password)
    user.password = hash_user_pass
    db_user = User(name=user.name, email=user.email, password=user.password)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return {"message": f"Your account has been created successfully, {user.name}!"}



# login user:
@app.post("/login")
def login_user(user: loginData, session: Session = Depends(get_session)):
    user_data = session.exec(select(User).where(User.email == user.email)).first()
    if user_data:
        if verify_password(user.password, user_data.password):
            token = create_access_token({"sub": user_data.email})
            return token
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password! Please try again or create an account if you don't have one.")



@app.get("/profile")
def get_profile_data(user: User = Depends(get_access_user)):
    return {"name": user.name, "email": user.email}


@app.post("/tasks")
def create_task(task:Create_Task, user: User = Depends(get_access_user), session: Session = Depends(get_session)):
    db_task = Tasks(title=task.title, description=task.description, status=task.status, owner_id=user.id)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return {"message": f"{user.name}'s Task '{task.title}' has been created successfully!"}



@app.get("/tasks", response_model=list[Task_Response])
def get_user_tasks(user: User = Depends(get_access_user), session: Session = Depends(get_session)):
    user_tasks = session.exec(select(Tasks).order_by(Tasks.id).where(Tasks.owner_id == user.id)).all()
    if user_tasks:
        return user_tasks
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="You don't have any tasks yet! Please create a task to see it here.")


# filter tasks by status: order_by(Tasks.id):
@app.get("/tasks/filter", response_model=list[Task_Response])
def filter_task_by_status(task_status: Literal["pending", "in progress", "completed"] = "pending", user: User = Depends(get_access_user), session: Session = Depends(get_session)):
    tasks = session.exec(select(Tasks).order_by(Tasks.id).where(Tasks.owner_id == user.id, Tasks.status == task_status)).all()
    if tasks:
        return tasks
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"You don't have any '{task_status}' tasks yet!")
    


# update task:
@app.put("/tasks/update/{task_id}")
def update_task_by_id(task_id: int, update_task:Update_task, user: User = Depends(get_access_user), session: Session = Depends(get_session)):
    db_task: Tasks = session.exec(select(Tasks).where(Tasks.owner_id == user.id, Tasks.id == task_id)).first()
    if not db_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"You don't have any task with this id: {task_id}!")
    if update_task.title:
        db_task.title = update_task.title
    if update_task.description:
        db_task.description = update_task.description
    if update_task.status:
        db_task.status = update_task.status
    
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return {"message": f"{user.name}'s Task '{db_task.title}' has been updated successfully!"}



# delete task:
@app.delete("/tasks/delete/{task_id}")
def delete_task_by_id(task_id: int, user: User = Depends(get_access_user), session: Session = Depends(get_session)):
    db_task : Tasks = session.exec(select(Tasks).where(Tasks.id == task_id, Tasks.owner_id == user.id))
    if not db_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"You don't have any task with this id: {task_id}!")
    session.delete(db_task)
    session.commit()
    return {"message": f"{user.name}'s Task with id: {task_id} has been deleted successfully!"}
