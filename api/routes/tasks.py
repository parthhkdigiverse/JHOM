from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime
from beanie import PydanticObjectId

from database.models import Task, Admin
from schemas.task import TaskCreate, TaskUpdate, TaskResponse
from utils.auth import get_current_admin

router = APIRouter()

# ==========================================
#  ROUTES
# ==========================================

@router.get("/", response_model=List[TaskResponse])
async def get_all_tasks(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = None,
    current_user: Admin = Depends(get_current_admin)
):
    """Get all tasks with optional filters from MongoDB"""
    query = Task.find_all()
    if status_filter:
        query = query.find(Task.status == status_filter)
    
    # We use fetch_links to populate creator and assignee
    return await query.skip(skip).limit(limit).to_list()

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: PydanticObjectId,
    current_user: Admin = Depends(get_current_admin)
):
    """Get a specific task by ID from MongoDB"""
    task = await Task.get(task_id, fetch_links=True)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    return task

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: Admin = Depends(get_current_admin)
):
    """Create a new task in MongoDB"""
    
    new_task = Task(
        title=task_data.title,
        description=task_data.description,
        status=task_data.status or "pending",
        deadline=datetime.fromisoformat(task_data.due_date) if task_data.due_date else datetime.utcnow(),
        created_by=current_user,
        assigned_to=current_user  # Default to self for now
    )
    
    await new_task.insert()
    return new_task

@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: PydanticObjectId,
    task_update: TaskUpdate,
    current_user: Admin = Depends(get_current_admin)
):
    """Update an existing task in MongoDB"""
    task = await Task.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    update_data = task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "due_date" and value:
            setattr(task, "deadline", datetime.fromisoformat(value))
        elif hasattr(task, field):
            setattr(task, field, value)
    
    task.updated_at = datetime.utcnow()
    await task.save()
    return task

@router.delete("/{task_id}")
async def delete_task(
    task_id: PydanticObjectId,
    current_user: Admin = Depends(get_current_admin)
):
    """Delete a task from MongoDB"""
    task = await Task.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    await task.delete()
    return {"status": "success", "message": "Task deleted"}