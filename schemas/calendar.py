"""
Pydantic Schemas for Calendar Events - Simplified Version
"""

from pydantic import BaseModel, field_validator, BeforeValidator
from datetime import datetime
from typing import Optional, Annotated
from beanie import PydanticObjectId
from schemas.auth import PyObjectId

class CalendarEventBase(BaseModel):
    title: str
    event_type: str  # appointment, meeting, work, task, event
    start_time: str  # Format: "2026-02-20 10:00"
    end_time: str    # Format: "2026-02-20 11:00"
    description: Optional[str] = None
    location: Optional[str] = None
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Title cannot be empty')
        return v.strip()
    
    @field_validator('event_type')
    @classmethod
    def validate_event_type(cls, v):
        valid_types = ["appointment", "meeting", "work", "task", "event"]
        if v.lower() not in valid_types:
            raise ValueError(f'Event type must be one of: {", ".join(valid_types)}')
        return v.lower()

class CalendarEventCreate(CalendarEventBase):
    pass

class CalendarEventUpdate(BaseModel):
    title: Optional[str] = None
    event_type: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None  # scheduled, completed, cancelled

class CalendarEventResponse(BaseModel):
    id: PyObjectId
    admin_id: Annotated[str, BeforeValidator(lambda v: str(v.id) if hasattr(v, 'id') else str(v))]
    title: str
    event_type: str
    start_time: datetime
    end_time: datetime
    description: Optional[str] = None
    location: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        populate_by_name = True