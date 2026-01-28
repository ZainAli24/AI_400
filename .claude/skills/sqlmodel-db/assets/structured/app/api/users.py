"""
User API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from app.db.database import get_session
from app.models.user import User, UserCreate, UserUpdate, UserPublic, UserWithTasks

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserPublic, status_code=201)
def create_user(user: UserCreate, session: Session = Depends(get_session)):
    """Create a new user"""
    try:
        db_user = User.model_validate(user)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=400,
            detail="User with this email or username already exists"
        )


@router.get("", response_model=list[UserPublic])
def get_users(
    skip: int = 0,
    limit: int = 20,
    is_active: bool | None = None,
    session: Session = Depends(get_session)
):
    """Get all users with optional filtering"""
    query = select(User)

    if is_active is not None:
        query = query.where(User.is_active == is_active)

    query = query.offset(skip).limit(limit).order_by(User.created_at.desc())

    return session.exec(query).all()


@router.get("/{user_id}", response_model=UserPublic)
def get_user(user_id: int, session: Session = Depends(get_session)):
    """Get a single user by ID"""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/{user_id}/with-tasks", response_model=UserWithTasks)
def get_user_with_tasks(user_id: int, session: Session = Depends(get_session)):
    """Get a user with all their tasks"""
    statement = (
        select(User)
        .options(selectinload(User.tasks))
        .where(User.id == user_id)
    )
    user = session.exec(statement).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=UserPublic)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    session: Session = Depends(get_session)
):
    """Update a user (partial update)"""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        update_data = user_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(user, key, value)

        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=400,
            detail="User with this email or username already exists"
        )


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, session: Session = Depends(get_session)):
    """Delete a user"""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    session.delete(user)
    session.commit()
