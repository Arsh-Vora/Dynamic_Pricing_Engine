from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ProductCreate(BaseModel):
    device_model: str
    condition: str
    age_in_months: int

class ProductResponse(BaseModel):
    id: int
    device_model: str
    condition: str
    age_in_months: int
    status: str
    initial_offer_price: float
    current_market_price: Optional[float] = None # NEW
    sold_at: Optional[datetime] = None # NEW (Nullable)
    created_at: datetime

    class Config:
        from_attributes = True
