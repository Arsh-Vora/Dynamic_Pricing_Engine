from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    device_model = Column(String, index=True)
    condition = Column(String)
    age_in_months = Column(Integer)
    status = Column(String)
    initial_offer_price = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
