from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate

def get_task(db: Session, task_id: int):
    return db.query(Task).filter(Task.id == task_id).first()

def get_multi(db: Session, skip: int = 0, limit: int = 100) -> List[Task]:
    return db.query(Task).offset(skip).limit(limit).all()

def get_multi_by_assignee(db: Session, assignee_id: int, skip: int = 0, limit: int = 100) -> List[Task]:
    return db.query(Task).filter(Task.assignee_id == assignee_id).offset(skip).limit(limit).all()

def create_assigned_task(db: Session, obj_in: TaskCreate, assigned_by_id: int) -> Task:
    db_obj = Task(
        title=obj_in.title,
        description=obj_in.description,
        status=obj_in.status,
        assignee_id=obj_in.assignee_id,
        assigned_by_id=assigned_by_id
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_task(db: Session, db_obj: Task, obj_in: TaskUpdate) -> Task:
    update_data = obj_in.model_dump(exclude_unset=True)
    for field in update_data:
        setattr(db_obj, field, update_data[field])
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def remove_task(db: Session, task_id: int) -> Optional[Task]:
    obj = db.query(Task).get(task_id)
    if obj:
        db.delete(obj)
        db.commit()
    return obj
