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
    current_admin: Admin = Depends(get_current_admin)
):
    """Get all tasks with optional filters from MongoDB"""
    try:
        query = Task.find()
        if status_filter:
            query = query.find(Task.status == status_filter)
        
        tasks_list = await query.skip(skip).limit(limit).to_list()
        
        result = []
        for t in tasks_list:
            assignee_name = None
            if t.assigned_to:
                assignee = await t.assigned_to.fetch()
                if assignee:
                    assignee_name = assignee.username
            
            result.append({
                "id": str(t.id),
                "title": t.title,
                "description": t.description,
                "status": t.status,
                "priority": getattr(t, 'priority', 'medium'),
                "due_date": t.deadline.strftime("%Y-%m-%d %H:%M:%S") if t.deadline else None,
                "assigned_to": assignee_name,
                "created_at": t.created_at,
                "updated_at": t.updated_at
            })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: PydanticObjectId,
    current_user: Admin = Depends(get_current_admin)
):
    """Get a specific task by ID from MongoDB"""
    task = await Task.get(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    
    assignee_name = None
    if task.assigned_to:
        assignee = await task.assigned_to.fetch()
        if assignee:
            assignee_name = assignee.username

    return {
        "id": str(task.id),
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "priority": getattr(task, 'priority', 'medium'),
        "due_date": task.deadline.strftime("%Y-%m-%d %H:%M:%S") if task.deadline else None,
        "assigned_to": assignee_name,
        "created_at": task.created_at,
        "updated_at": task.updated_at
    }


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: Admin = Depends(get_current_admin)
):
    """Create a new task in MongoDB"""
    try:
        new_task = Task(
            title=task_data.title,
            description=task_data.description,
            status=task_data.status or "pending",
            priority=task_data.priority or "medium",
            deadline=datetime.fromisoformat(task_data.due_date) if task_data.due_date else datetime.utcnow(),
            created_by=current_user,
            assigned_to=current_user
        )
        
        await new_task.insert()
        
        return {
            "id": str(new_task.id),
            "title": new_task.title,
            "description": new_task.description,
            "status": new_task.status,
            "priority": new_task.priority,
            "due_date": new_task.deadline.strftime("%Y-%m-%d %H:%M:%S"),
            "assigned_to": current_user.username,
            "created_at": new_task.created_at,
            "updated_at": new_task.updated_at
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
    
    assignee_name = None
    if task.assigned_to:
        assignee = await task.assigned_to.fetch()
        if assignee:
            assignee_name = assignee.username

    return {
        "id": str(task.id),
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "priority": getattr(task, 'priority', 'medium'),
        "due_date": task.deadline.strftime("%Y-%m-%d %H:%M:%S") if task.deadline else None,
        "assigned_to": assignee_name,
        "created_at": task.created_at,
        "updated_at": task.updated_at
    }



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