from pydantic import BaseModel
from typing import List

class ProductItem(BaseModel):
    name: str
    quantity: str
    packaging: str
    grade: str
    origin: str
    price: float

class QuotePayload(BaseModel):
    products: List[ProductItem]
    price_term: str
    advance_pct: int
    balance_pct: int
    delivery_mode: str
    timeline: str
