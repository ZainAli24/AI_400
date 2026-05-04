from fastapi import FastAPI, Depends, status, HTTPException
from sqlmodel import SQLModel, Session, create_engine, select, Field
from dotenv import load_dotenv
import os
from datetime import datetime
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

password_hash = PasswordHash((Argon2Hasher(), ))


load_dotenv(".env")


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
    if session.exec(select(User).where(User.email == user.email)).first():
        user_data = session.exec(select(User).where(User.email == user.email)).first()
        if verify_password(user.password, user_data.password):
            return {"message": f"Welcome back, {user_data.name}!"}
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password! Please try again or create an account if you don't have one.")


