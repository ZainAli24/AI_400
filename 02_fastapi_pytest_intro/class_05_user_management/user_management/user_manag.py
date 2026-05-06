from fastapi import FastAPI, Depends, status, HTTPException
from sqlmodel import SQLModel, Session, create_engine, select, Field
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from jose import jwt, JWTError, ExpiredSignatureError
from typing import Optional
from fastapi.security import OAuth2PasswordBearer

acccess_token = OAuth2PasswordBearer(tokenUrl="login")


password_hash = PasswordHash((Argon2Hasher(), ))


SECRET_KEY="Zain123321"
ALOGRITHUM="HS256"


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


# Create JWT Token:
def create_access_token(user_data: dict, expire_time: Optional[timedelta] = None):
    encode_data = user_data.copy()
    expire = datetime.utcnow() + (expire_time or timedelta(minutes=5))
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
    if session.exec(select(User).where(User.email == user.email)).first():
        user_data = session.exec(select(User).where(User.email == user.email)).first()
        if verify_password(user.password, user_data.password):
            token = create_access_token({"sub": user_data.email})
            return token
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password! Please try again or create an account if you don't have one.")



@app.get("/profile")
def get_profile_data(user: User = Depends(get_access_user)):
    return {"name": user.name, "email": user.email}

