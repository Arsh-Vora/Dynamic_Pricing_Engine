import os
import json
import google.generativeai as genai
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

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

    # Gemini API Integration
    try:
        prompt = f"Given a {product.device_model} in {product.condition} condition, that is {product.age_in_months} months old, what is a fair market price? Respond with only a JSON object containing a single key 'price' and its float value. Example: {{"price": 123.45}}"
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        llm_output = json.loads(response.text)
        offer_price = float(llm_output.get("price", 0.0))

        db_product.initial_offer_price = offer_price
        db.add(db_product)
        db.commit()
        db.refresh(db_product)

    except Exception as e:
        print(f"Error calling Gemini API or parsing response: {e}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Failed to get valuation from AI service.")

    return db_product
