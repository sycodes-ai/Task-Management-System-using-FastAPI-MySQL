from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from app.schemas.task import TaskResponse

class UserBase(BaseModel):
    custom_username: str
    email: EmailStr
    role: Optional[str] = "staff"

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    # Omitting tasks list from the generic response to simplify relationships for now
    
    class Config:
        from_attributes = True
