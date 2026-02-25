from pydantic import BaseModel
from typing import Optional
from datetime import datetime

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
