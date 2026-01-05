from fastapi import APIRouter, HTTPException
from typing import List
from app.models.user import UserCreate, UserUpdate, UserInDB

router = APIRouter()

# Mock database
fake_users_db = {}
user_id_counter = 1


@router.get("/", response_model=List[UserInDB])
def get_users(skip: int = 0, limit: int = 10):
    users = list(fake_users_db.values())
    return users[skip : skip + limit]


@router.get("/{user_id}", response_model=UserInDB)
def get_user(user_id: int):
    if user_id not in fake_users_db:
        raise HTTPException(status_code=404, detail="User not found")
    return fake_users_db[user_id]


@router.post("/", response_model=UserInDB, status_code=201)
def create_user(user: UserCreate):
    global user_id_counter
    # In production, hash the password before storing
    user_dict = user.model_dump()
    user_dict.pop("password")  # Don't store password in this example
    user_in_db = UserInDB(id=user_id_counter, **user_dict)
    fake_users_db[user_id_counter] = user_in_db
    user_id_counter += 1
    return user_in_db


@router.put("/{user_id}", response_model=UserInDB)
def update_user(user_id: int, user: UserUpdate):
    if user_id not in fake_users_db:
        raise HTTPException(status_code=404, detail="User not found")

    stored_user = fake_users_db[user_id]
    update_data = user.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data.pop("password")  # Don't update password in this example
    updated_user = stored_user.model_copy(update=update_data)
    fake_users_db[user_id] = updated_user
    return updated_user


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int):
    if user_id not in fake_users_db:
        raise HTTPException(status_code=404, detail="User not found")
    del fake_users_db[user_id]
