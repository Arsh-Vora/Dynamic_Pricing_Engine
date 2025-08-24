from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db

router = APIRouter(
    prefix="/products",
    tags=["products"]
)

@router.post("/register", response_model=schemas.ProductResponse, status_code=status.HTTP_201_CREATED)
def register_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    # initial_offer_price will be calculated by the pricing engine in a future feature.
    # For now, setting it to 0.0 as a placeholder.
    db_product = models.Product(
        device_model=product.device_model,
        condition=product.condition,
        age_in_months=product.age_in_months,
        status="Registered",
        initial_offer_price=0.0 # Placeholder for future dynamic pricing
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product
