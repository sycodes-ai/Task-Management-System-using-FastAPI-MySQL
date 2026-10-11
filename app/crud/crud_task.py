from sqlalchemy import func, or_
from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Tuple
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate

def get_task(db: Session, task_id: int):
    return db.query(Task).filter(Task.id == task_id).first()

def _apply_filters(
    query,
    assignee_id: Optional[int] = None,
    status: Optional[str] = None,
    q: Optional[str] = None,
):
    if assignee_id is not None:
        query = query.filter(Task.assignee_id == assignee_id)
    if status is not None:
        query = query.filter(Task.status == status)
    if q:
        # "/" as the LIKE escape character (a backslash needs extra care on MySQL)
        escaped = q.replace("/", "//").replace("%", "/%").replace("_", "/_")
        pattern = f"%{escaped}%"
        query = query.filter(
            or_(
                Task.title.ilike(pattern, escape="/"),
                Task.description.ilike(pattern, escape="/"),
            )
        )
    return query

def get_multi_filtered(
    db: Session,
    *,
    assignee_id: Optional[int] = None,
    status: Optional[str] = None,
    q: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    sort: str = "-created_at",
) -> Tuple[List[Task], int]:
    """Return one page of matching tasks and the total number of matches."""
    query = _apply_filters(db.query(Task), assignee_id=assignee_id, status=status, q=q)
    total = query.count()
    # id is a tie-breaker: created_at only has one-second precision on some databases
    if sort == "created_at":
        query = query.order_by(Task.created_at.asc(), Task.id.asc())
    else:
        query = query.order_by(Task.created_at.desc(), Task.id.desc())
    return query.offset(skip).limit(limit).all(), total

def get_status_counts(db: Session, assignee_id: Optional[int] = None) -> Dict[str, int]:
    query = db.query(Task.status, func.count(Task.id))
    if assignee_id is not None:
        query = query.filter(Task.assignee_id == assignee_id)
    rows = query.group_by(Task.status).all()
    counts = {"pending": 0, "in_progress": 0, "completed": 0}
    counts.update({status: count for status, count in rows})
    counts["total"] = sum(counts.values())
    return counts

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
    obj = db.get(Task, task_id)
    if obj:
        db.delete(obj)
        db.commit()
    return obj
