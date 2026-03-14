from pydantic import BaseModel
from typing import List, Optional

class ProformaItem(BaseModel):
    sr_no: int
    description: str
    hs_code: str
    packaging: str
    quantity: str
    origin: str
    rate: float
    total: float

class ProformaPayload(BaseModel):
    id: str
    date: str
    lc_date: str
    validity: str
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
