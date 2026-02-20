from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# -----------------
# Task Schemas
# -----------------
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    is_completed: bool = False

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_completed: Optional[bool] = None

class TaskResponse(TaskBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# -----------------
# User Schemas
# -----------------
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
