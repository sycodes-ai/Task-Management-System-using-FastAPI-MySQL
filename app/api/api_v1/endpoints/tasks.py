from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import deps
from app.crud import crud_task, crud_user

router = APIRouter()

@router.get("/", response_model=List[schemas.TaskResponse])
def read_tasks(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve tasks. Admins see all, Staff see assigned.
    """
    if current_user.role == "admin":
        tasks = crud_task.get_multi(db, skip=skip, limit=limit)
    else:
        tasks = crud_task.get_multi_by_assignee(db, assignee_id=current_user.id, skip=skip, limit=limit)
    return tasks

@router.post("/", response_model=schemas.TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    *,
    db: Session = Depends(deps.get_db),
    task_in: schemas.TaskCreate,
    current_admin: models.User = Depends(deps.get_current_admin),
) -> Any:
    """
    Create new task. (Admin only)
    """
    if not crud_user.get_user(db, user_id=task_in.assignee_id):
        raise HTTPException(status_code=404, detail="Assignee not found")
    return crud_task.create_assigned_task(db, obj_in=task_in, assigned_by_id=current_admin.id)

@router.get("/{task_id}", response_model=schemas.TaskResponse)
def read_task(
    *,
    db: Session = Depends(deps.get_db),
    task_id: int,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Get task by ID.
    """
    task = crud_task.get_task(db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if current_user.role != "admin" and task.assignee_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return task

@router.put("/{task_id}", response_model=schemas.TaskResponse)
def update_task(
    *,
    db: Session = Depends(deps.get_db),
    task_id: int,
    task_in: schemas.TaskUpdate,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Update a task. Staff can only update status. Admins can update all fields.
    """
    task = crud_task.get_task(db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    if current_user.role == "staff":
        if task.assignee_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        # Staff may only change the status. Other fields are allowed in the body
        # as long as they match the stored values.
        changed = {
            field for field, value in task_in.model_dump(exclude_unset=True).items()
            if field != "status" and getattr(task, field) != value
        }
        if changed:
            raise HTTPException(status_code=403, detail="Staff can only update the task status")
        if task_in.status is None:
            raise HTTPException(status_code=422, detail="Status is required")
        task_in = schemas.TaskUpdate(status=task_in.status)
    elif task_in.assignee_id is not None and task_in.assignee_id != task.assignee_id:
        if not crud_user.get_user(db, user_id=task_in.assignee_id):
            raise HTTPException(status_code=404, detail="Assignee not found")

    return crud_task.update_task(db, db_obj=task, obj_in=task_in)

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    *,
    db: Session = Depends(deps.get_db),
    task_id: int,
    current_admin: models.User = Depends(deps.get_current_admin),
):
    """
    Delete a task. (Admin only)
    """
    task = crud_task.get_task(db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    crud_task.remove_task(db, task_id=task_id)
