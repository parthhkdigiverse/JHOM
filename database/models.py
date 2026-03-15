"""
Database Models - Beanie/MongoDB version
"""

from typing import Optional, List
from datetime import datetime
from beanie import Document, Indexed, Link
from pydantic import Field, EmailStr

class Admin(Document):
    """Admin/User model for authentication"""
    username: Indexed(str, unique=True)
    password: str
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: str = "admin"  # superuser or admin
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "admins"

class Buyer(Document):
    """Buyer model matching frontend fields"""
    name: str
    company_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = "India"
    gst_number: Optional[str] = None
    payment_terms: str  # FOB or CIF
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "buyers"

class Manufacturer(Document):
    """Manufacturer model matching frontend fields"""
    name: str
    company_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = "India"
    gst_number: Optional[str] = None
    product_category: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "manufacturers"

class Task(Document):
    """Task model"""
    title: str
    description: Optional[str] = None
    created_by: Link[Admin]
    assigned_to: Link[Admin]
    deadline: datetime
    status: Indexed(str) = "pending"
    priority: str = "medium"
    created_at: datetime = Field(default_factory=datetime.utcnow)

    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "tasks"

class CalendarEvent(Document):
    """Calendar Event model"""
    admin_id: Link[Admin]
    title: str
    description: Optional[str] = None
    event_type: Indexed(str)
    start_time: Indexed(datetime)
    end_time: Indexed(datetime)
    location: Optional[str] = None
    status: Indexed(str) = "scheduled"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "calendar_events"