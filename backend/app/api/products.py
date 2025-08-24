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
    # For now, let's set a dummy initial_offer_price
    # In a real scenario, this would be calculated by the pricing engine
    dummy_initial_offer_price = 100.00 # Example value

    db_product = models.Product(
        device_model=product.device_model,
        condition=product.condition,
        age_in_months=product.age_in_months,
        status="Registered",
        initial_offer_price=dummy_initial_offer_price
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product
