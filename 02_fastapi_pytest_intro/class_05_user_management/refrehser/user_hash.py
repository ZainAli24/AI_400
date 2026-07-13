from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import SQLModel, select, create_engine, Session, Field
from pydantic_settings import BaseSettings
import os
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from functools import lru_cache

app = FastAPI()


class Variables(BaseSettings):
    DATABASE_URL: str

    class Config:
        env_file = ".env"


password_hasher = PasswordHash((Argon2Hasher(), ))

def hash_password(password: str) -> str:
    hashed_pass = password_hasher.hash(password)
    return hashed_pass


def verify_password(plain_pass: str, hashed_pass: str) -> str:
    is_correct = password_hasher.verify(plain_pass, hashed_pass)
    return is_correct



class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: str
    password: str


class User_input(SQLModel):
    name: str
    email: str
    password: str


class User_login(SQLModel):
    email: str
    password: str

@lru_cache
def get_variable():
    return Variables()


# create engine:

engine = create_engine(url=get_variable().DATABASE_URL, echo=True)


# table creation:
# def create_table():
#     print("\n\n Trying To Creating User Table ....\n\n")
#     SQLModel.metadata.create_all(engine)
#     print("\n\n Table Created Successfully!!")


# create_table()



# session:
def get_session():
    with Session(engine) as session:
        yield session



# create user:
@app.post("/users/create")
def create_user(user: User_input, session: Session = Depends(get_session)):
    db_user = session.exec(select(User).where(User.email == user.email)).first()
    if db_user:
        raise HTTPException(status_code=401, detail="User already exist!")
    
    user.password = hash_password(user.password)
    actual_user = User.model_validate(user)
    session.add(actual_user)
    session.commit()
    session.refresh(actual_user)
    return {"message": f"User {actual_user.name} created Successfully!"}


# login user:
@app.post("/users/login")
def login_user(user_data: User_login, session: Session = Depends(get_session)):
    db_user: User = session.exec(select(User).where(User.email == user_data.email)).first()
    if db_user:
        is_correct = verify_password(user_data.password, db_user.password)
        if is_correct:
            return {"message": "Login Successfully!"}
        else: 
            raise HTTPException(status_code=401, detail="Password Incorrect!!")
    else:
        raise HTTPException(status_code=404, detail="User Not Found!!")
    

