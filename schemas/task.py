"""
Pydantic Schemas for Task
"""

from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, Annotated
from beanie import PydanticObjectId
from schemas.auth import PyObjectId

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[str] = "pending"
    priority: Optional[str] = "medium"
    due_date: Optional[str] = None
    assigned_to: Optional[str] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[str] = None
    assigned_to: Optional[str] = None

class TaskResponse(TaskBase):
    id: PyObjectId
    assigned_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)