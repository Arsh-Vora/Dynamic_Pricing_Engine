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
    created_at: datetime

    class Config:
        from_attributes = True
