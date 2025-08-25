from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from .database import engine # <-- ADD THIS LINE

Base = declarative_base()

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    device_model = Column(String, index=True)
    condition = Column(String)
    age_in_months = Column(Integer)
    status = Column(String)
    initial_offer_price = Column(Float)
    current_market_price = Column(Float, nullable=True) # NEW
    sold_at = Column(DateTime(timezone=True), nullable=True) # NEW (Nullable)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
