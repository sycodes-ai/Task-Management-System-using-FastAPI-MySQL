from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints
from typing import Annotated, Literal
from datetime import datetime

class UserBase(BaseModel):
    custom_username: str
    email: EmailStr

class UserCreate(UserBase):
    # No role field: registration always creates a staff user
    custom_username: Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=50)]
    password: str = Field(min_length=8)

class UserResponse(UserBase):
    id: int
    role: Literal["admin", "staff"]
    is_active: bool
    created_at: datetime
    # Omitting tasks list from the generic response to simplify relationships for now

    model_config = ConfigDict(from_attributes=True)
