from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import SQLModel, Field, create_engine, Session, select   # type: ignore
from dotenv import load_dotenv
import os

load_dotenv()

from pwdlib import PasswordHash   # type: ignore
from pwdlib.hashers.argon2 import Argon2Hasher  # type: ignore


hash_password = PasswordHash((Argon2Hasher(), ))

def password_hasher(password: str) -> str:
    """Hash a plain password."""
    return hash_password.hash(password)


def verify_password(plain_password: str , hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return hash_password.verify(plain_password, hashed_password)


# -------------------------------------------------------

from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError

SECRET_KEY="your_secret_key"
ALGORITHM="HS256"


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed JWT token."""
    to_encode = data.copy()

    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))

    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT token."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


# -------------------------------------------------------
# OAuth2PasswordBearer Setup
# -------------------------------------------------------

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# -------------------------------------------------------

# first we need to create the engine to manage the connection with the database.

engine = create_engine(os.getenv("DATABASE_URL"), echo=True) # echo=True debugging purpose only, it will log all the sql statements executed, logs will be shown on the terminal/console.


app = FastAPI()


# This Class used to create the table structure in the DB and also used as Pydantic model for data validation in request body of create_task API.
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)  # primary key defines unique identity for each record/row in the table
    username: str
    email: str 
    password: str



#  1. first we need to create the tables in the database using SQLModel
# def create_tables():
#     print("---------------- Creating Tables in the Database -------------------")
#     SQLModel.metadata.create_all(engine) 
#     print("---------------- Tables created successfully! -------------------")

# create_tables()

# -------------------------------------------------------

# 2. How to actually interact with tables in the database?

# Session is used to manage the transactions with the database ( like insert, update, delete, select ).

def get_session():
    with Session(engine) as session:
        yield session


# Create User in the database
@app.post("/users")
def create_user(user: User , session: Session = Depends(get_session)):
    # check if user with same email already exists
    if session.exec(select(User).where(User.email == user.email)).first():          # .first() = Pehla result do, agar nahi to None
        raise HTTPException(status_code=400, detail="User already exists")
    
    user.password = password_hasher(user.password) # hash the password before storing it in the database
    session.add(user)
    session.commit()
    print("------------------ User created:", user ,"-------------------")
    session.refresh(user)
    return {"message": "User created successfully!"}

# In if-else condition, None is considered as False.    


# login user
@app.post("/login")
def login_user(email: str, password: str, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == email)).first()
    if user and verify_password(password, user.password):
        token = create_access_token({"sub": user.email})
        return {"token_type": "bearer", "access_token": token}
    raise HTTPException(status_code=401, detail="Invalid email or password")


# -------------------------------------------------------
# Protected Endpoint - Get Current User (Token Required)
# -------------------------------------------------------

@app.get("/users/me")
def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
):
    # Step 1: Token decode karo
    payload = decode_token(token)

    # Step 2: Agar token invalid hai toh error
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Step 3: Payload se email nikalo
    email = payload.get("sub")

    # Step 4: Database se user dhundo
    user = session.exec(select(User).where(User.email == email)).first()

    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    # Step 5: User data return karo
    return {"id": user.id, "username": user.username, "email": user.email}


