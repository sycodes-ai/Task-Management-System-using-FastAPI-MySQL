from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from app.schemas.task import TaskResponse

class UserBase(BaseModel):
    custom_username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    tasks: List[TaskResponse] = []

    class Config:
        from_attributes = True
