from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.user import User as UserModel
from app.schemas.user import User, UserCreate, UserUpdate

router = APIRouter()


def fake_hash_password(password: str):
    """In production, use proper password hashing like bcrypt"""
    return f"hashed_{password}"


@router.get("/", response_model=List[User])
def get_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    users = db.query(UserModel).offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=User)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/", response_model=User, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    db_user = db.query(UserModel).filter(UserModel.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user_dict = user.model_dump()
    password = user_dict.pop("password")
    db_user = UserModel(**user_dict, hashed_password=fake_hash_password(password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.put("/{user_id}", response_model=User)
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user.model_dump(exclude_unset=True)
    if "password" in update_data:
        password = update_data.pop("password")
        update_data["hashed_password"] = fake_hash_password(password)

    for field, value in update_data.items():
        setattr(db_user, field, value)

    db.commit()
    db.refresh(db_user)
    return db_user


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(db_user)
    db.commit()
