from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator
from typing import Annotated, Literal, Optional
from datetime import datetime

TaskStatus = Literal["pending", "in_progress", "completed"]
TaskTitle = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
TaskDescription = Annotated[str, Field(max_length=255)]

class TaskBase(BaseModel):
    title: TaskTitle
    description: Optional[TaskDescription] = None
    status: TaskStatus = "pending"

class TaskCreate(TaskBase):
    assignee_id: int

class TaskUpdate(BaseModel):
    title: Optional[TaskTitle] = None
    description: Optional[TaskDescription] = None
    status: Optional[TaskStatus] = None
    assignee_id: Optional[int] = None

    @field_validator("title", "status", "assignee_id")
    @classmethod
    def not_null(cls, value):
        # Fields may be omitted, but an explicit null would break NOT NULL columns
        if value is None:
            raise ValueError("may not be null")
        return value

class TaskResponse(TaskBase):
    # Return stored values as they are; the input limits apply to requests only
    title: str
    description: Optional[str] = None
    id: int
    assignee_id: int
    assigned_by_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class TaskStats(BaseModel):
    pending: int
    in_progress: int
    completed: int
    total: int
