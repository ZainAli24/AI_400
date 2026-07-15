from fastapi import FastAPI, Depends, HTTPException, status
from sqlmodel import SQLModel, select, create_engine, Session, Field
from pydantic_settings import BaseSettings
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from functools import lru_cache
from jose import jwt, JWTError, ExpiredSignatureError
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi.security import OAuth2PasswordBearer


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


app = FastAPI()


class Variables(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALOGRITHUM: str

    class Config:
        env_file = ".env"



@lru_cache
def get_variable():
    return Variables()


password_hasher = PasswordHash((Argon2Hasher(), ))

def hash_password(password: str) -> str:
    hashed_pass = password_hasher.hash(password)
    return hashed_pass


def verify_password(plain_pass: str, hashed_pass: str) -> str:
    is_correct = password_hasher.verify(plain_pass, hashed_pass)
    return is_correct



def create_access_token(data: dict, time: Optional[timedelta] = None):
    encode_data = data.copy()
 
    expire_time = datetime.now(timezone.utc) + (time or timedelta(minutes=15))

    encode_data.update({"exp": expire_time})

    token = jwt.encode(encode_data, get_variable().SECRET_KEY, algorithm=get_variable().ALOGRITHUM)

    return token



def verify_token(token: str):
    try:
        payload = jwt.decode(token, get_variable().SECRET_KEY, algorithms=[get_variable().ALOGRITHUM])
        return payload
    except ExpiredSignatureError:
        return "expired"
    except JWTError:
        return None
    




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




def get_current_user(token = Depends(oauth2_scheme), session: Session = Depends(get_session))-> User:

    credentail_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    credentail_expire_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token Expired, Please Login Again!",
        headers={"WWW-Authenticate": "Bearer"},
    )


    payload = verify_token(token)

    if payload == "expired":
        raise credentail_expire_exception
    
    if payload == None:
        raise credentail_exception
    
    email = payload.get("sub")

    if email:
        db_user = session.exec(select(User).where(User.email == email)).first()
        if db_user:
            return db_user
        else:
            raise credentail_exception
    else:
        raise credentail_exception



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
            return {"token_type": "bearer", "access_token": create_access_token({"sub": db_user.email})}
        else: 
            raise HTTPException(status_code=401, detail="Password Incorrect!!")
    else:
        raise HTTPException(status_code=404, detail="User Not Found!!")
    



# get user:
@app.get("/profile")
def get_user(current_user: User = Depends(get_current_user)):

    return {"name": current_user.name, "email": current_user.email}

