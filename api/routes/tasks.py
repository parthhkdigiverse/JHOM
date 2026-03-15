from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime
from beanie import PydanticObjectId

from database.models import Task, Admin
from schemas.task import TaskCreate, TaskUpdate, TaskResponse
from utils.auth import get_current_admin

router = APIRouter()

# ==========================================
#  HELPERS
# ==========================================

async def get_assignee_info(task: Task):
    """Fetch assignee details and return (username, full_name)"""
    username = None
    full_name = None
    if task.assigned_to:
        # Check if it's already a document or a link
        if hasattr(task.assigned_to, "fetch"):
            assignee = await task.assigned_to.fetch()
        else:
            assignee = task.assigned_to
            
        if assignee:
            username = assignee.username
            full_name = assignee.full_name or assignee.username
    return username, full_name

def format_task_response(task: Task, username: str, full_name: str):
    """Unified task response formatter"""
    return {
        "id": str(task.id),
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "priority": getattr(task, 'priority', 'medium'),
        "due_date": task.deadline.strftime("%Y-%m-%d %H:%M:%S") if task.deadline else None,
        "assigned_to": username,
        "assigned_name": full_name,
        "created_at": task.created_at,
        "updated_at": task.updated_at
    }

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
            u, f = await get_assignee_info(t)
            result.append(format_task_response(t, u, f))
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
    
    u, f = await get_assignee_info(task)
    return format_task_response(task, u, f)


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: Admin = Depends(get_current_admin)
):
    """Create a new task in MongoDB"""
    try:
        # Handle assigned_to
        assignee = current_user
        if task_data.assigned_to:
            found_admin = await Admin.find_one(Admin.username == task_data.assigned_to)
            if found_admin:
                assignee = found_admin
        
        # Parse deadline safely
        deadline = datetime.utcnow()
        if task_data.due_date:
            try:
                # Remove T and handle various formats
                dt_str = task_data.due_date.replace('T', ' ')
                if len(dt_str) == 10: # YYYY-MM-DD
                    deadline = datetime.strptime(dt_str, "%Y-%m-%d")
                else:
                    deadline = datetime.fromisoformat(task_data.due_date.replace(' ', 'T'))
            except:
                deadline = datetime.utcnow()

        new_task = Task(
            title=task_data.title,
            description=task_data.description,
            status=task_data.status or "pending",
            priority=task_data.priority or "medium",
            deadline=deadline,
            created_by=current_user,
            assigned_to=assignee
        )
        
        await new_task.insert()
        
        return format_task_response(new_task, assignee.username, assignee.full_name or assignee.username)
    except Exception as e:
        print(f"Error creating task: {str(e)}")
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
            try:
                dt_str = value.replace('T', ' ')
                if len(dt_str) == 10:
                    setattr(task, "deadline", datetime.strptime(dt_str, "%Y-%m-%d"))
                else:
                    setattr(task, "deadline", datetime.fromisoformat(value.replace(' ', 'T')))
            except:
                pass
        elif field == "assigned_to" and value:
            assignee = await Admin.find_one(Admin.username == value)
            if assignee:
                task.assigned_to = assignee
        elif hasattr(task, field):
            setattr(task, field, value)
    
    task.updated_at = datetime.utcnow()
    await task.save()
    
    u, f = await get_assignee_info(task)
    return format_task_response(task, u, f)



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