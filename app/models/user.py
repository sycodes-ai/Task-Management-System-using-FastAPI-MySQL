from sqlalchemy import Boolean, Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    custom_username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(255))
    is_active = Column(Boolean, default=True)
    role = Column(Enum('admin', 'staff', name='user_roles'), default='staff', nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship to tasks
    tasks_assigned_to_me = relationship("Task", back_populates="assignee", foreign_keys="[Task.assignee_id]")
    tasks_assigned_by_me = relationship("Task", back_populates="assigned_by", foreign_keys="[Task.assigned_by_id]")
