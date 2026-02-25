from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate

def get_task(db: Session, task_id: int):
    return db.query(Task).filter(Task.id == task_id).first()

def get_multi_by_owner(db: Session, owner_id: int, skip: int = 0, limit: int = 100) -> List[Task]:
    return db.query(Task).filter(Task.owner_id == owner_id).offset(skip).limit(limit).all()

def create_with_owner(db: Session, obj_in: TaskCreate, owner_id: int) -> Task:
    db_obj = Task(
        **obj_in.model_dump(),
        owner_id=owner_id
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
