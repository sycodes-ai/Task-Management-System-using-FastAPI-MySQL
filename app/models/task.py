from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), index=True)
    description = Column(String(255), index=True, nullable=True)
    status = Column(Enum('pending', 'in_progress', 'completed', name='task_status'), default='pending', nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Foreign key link back to the User table
    assignee_id = Column(Integer, ForeignKey("users.id"))
    assigned_by_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationship to user
    assignee = relationship("User", back_populates="tasks_assigned_to_me", foreign_keys=[assignee_id])
    assigned_by = relationship("User", back_populates="tasks_assigned_by_me", foreign_keys=[assigned_by_id])
