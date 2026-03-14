"""
Pydantic Schemas for Buyer
"""

from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime
from typing import Optional
from beanie import PydanticObjectId

class BuyerBase(BaseModel):
    name: str
    company_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = "India"
    gst_number: Optional[str] = None
    payment_terms: str
    is_active: bool = True

    @field_validator('payment_terms')
    @classmethod
    def validate_terms(cls, v):
        if v.upper() not in ["FOB", "CIF"]:
            raise ValueError('Terms must be either "FOB" or "CIF"')
        return v.upper()

class BuyerCreate(BuyerBase):
    pass

class BuyerUpdate(BaseModel):
    name: Optional[str] = None
    company_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    gst_number: Optional[str] = None
    payment_terms: Optional[str] = None
    is_active: Optional[bool] = None

class BuyerResponse(BuyerBase):
    id: PydanticObjectId
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)