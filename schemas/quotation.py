from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class ProductItem(BaseModel):
    name: str
    quantity: str
    packaging: str
    grade: str
    origin: str
    price: float

class QuotePayload(BaseModel):
    buyer_id: Optional[str] = None
    products: List[ProductItem]
    price_term: str
    advance_pct: int
    balance_pct: int
    delivery_mode: str
    timeline: str

class QuotationResponse(BaseModel):
    id: str
    buyer_id: Optional[str] = None
    products: List[ProductItem]
    price_term: str
    advance_pct: int
    balance_pct: int
    delivery_mode: str
    timeline: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
