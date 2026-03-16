from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class ProformaItem(BaseModel):
    description: str
    hs_code: str
    packaging: str
    quantity: str
    origin: str
    rate: float
    total: float

class ProformaPayload(BaseModel):
    invoice_no: str
    date: str
    lc_date: Optional[str] = None
    validity: Optional[str] = None
    buyer_id: str
    buyer_name: str
    buyer_address: str
    products: List[ProformaItem]
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

class ProformaInvoiceResponse(BaseModel):
    id: str
    invoice_no: str
    date: str
    lc_date: Optional[str] = None
    validity: Optional[str] = None
    buyer_id: str
    buyer_name: str
    buyer_address: str
    products: List[ProformaItem]
    incoterm: str
    currency: str
    advance_pct: int
    balance_pct: int
    mode_of_shipment: str
    delivery_time: str
    port_of_loading: str
    port_of_discharge: str
    amount_in_words: str
    grand_total: float
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
