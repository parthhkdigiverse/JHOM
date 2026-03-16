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

class Quotation(Document):
    """Quotation model"""
    buyer_id: Optional[Link[Buyer]] = None
    products: List[dict] # List of ProductItem-like dicts
    price_term: str
    advance_pct: int
    balance_pct: int
    delivery_mode: str
    timeline: str
    status: str = "draft" # draft, sent, converted
    created_by: Link[Admin]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "quotations"

class ProformaInvoice(Document):
    """Proforma Invoice model"""
    invoice_no: Indexed(str, unique=True)
    date: str
    lc_date: Optional[str] = None
    validity: Optional[str] = None
    buyer_id: Link[Buyer]
    buyer_name: str # Snapshot in case buyer details change
    buyer_address: str
    products: List[dict] # List of ProformaItem-like dicts
    incoterm: str
    currency: str = "USD"
    advance_pct: int
    balance_pct: int
    mode_of_shipment: str
    delivery_time: str
    port_of_loading: str
    port_of_discharge: str
    amount_in_words: str
    grand_total: float
    status: str = "issued" # issued, paid, cancelled
    created_by: Link[Admin]
    quotation_id: Optional[Link[Quotation]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "proforma_invoices"