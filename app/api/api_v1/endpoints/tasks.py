from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import deps
from app.crud import crud_task

router = APIRouter()

@router.get("/", response_model=List[schemas.TaskResponse])
def read_tasks(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve tasks.
    """
    tasks = crud_task.get_multi_by_owner(db, owner_id=current_user.id, skip=skip, limit=limit)
    return tasks

@router.post("/", response_model=schemas.TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    *,
    db: Session = Depends(deps.get_db),
    task_in: schemas.TaskCreate,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Create new task.
    """
    return crud_task.create_with_owner(db, obj_in=task_in, owner_id=current_user.id)

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
    if task.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
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
    Update a task.
    """
    task = crud_task.get_task(db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return crud_task.update_task(db, db_obj=task, obj_in=task_in)

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    *,
    db: Session = Depends(deps.get_db),
    task_id: int,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Delete a task.
    """
    task = crud_task.get_task(db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    crud_task.remove_task(db, task_id=task_id)
    return None
