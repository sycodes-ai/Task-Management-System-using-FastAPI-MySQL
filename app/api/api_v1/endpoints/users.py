from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import deps
from app.crud import crud_user

router = APIRouter()

@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreate,
) -> Any:
    """
    Create new user.
    """
    user = crud_user.get_user_by_username(db, username=user_in.custom_username)
    if user:
        raise HTTPException(
            status_code=400,
            detail="Username already registered",
        )
    user = crud_user.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )
    return crud_user.create_user(db, obj_in=user_in)

@router.get("/me", response_model=schemas.UserResponse)
def get_me(
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Get current user.
    """
    return current_user
