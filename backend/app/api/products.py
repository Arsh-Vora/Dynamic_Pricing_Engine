import logging
import os
import json
import google.generativeai as genai
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

router = APIRouter(
    prefix="/products", # This adds the "/products" part of the URL
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
        prompt = f"Given a used {product.device_model} in {product.condition} condition, that is {product.age_in_months} months old, what is a fair second-hand market resale value, considering typical depreciation and wear and tear? Respond with only a JSON object containing a single key 'price' and its float value. Example: {{'price': 123.45}}"
        model = genai.GenerativeModel('gemini-2.5-flash')
        try:
            response = model.generate_content(prompt)
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="The valuation service is currently unavailable due to API issues.") from e

        # --- NEW DEBUGGING AND SAFETY CODE ---
        print("--- Full Gemini Response ---")
        print(response)
        # ------------------------------------
        
        # Check if the response is empty before trying to parse it
        if not response.text:
            # Here we can inspect the response object to find out why it was empty
            # The prompt_feedback object often contains the reason
            print("--- EMPTY RESPONSE RECEIVED FROM GEMINI ---")
            print(f"Prompt Feedback: {response.prompt_feedback}")
            raise ValueError("Received an empty response from the AI service, possibly due to content safety filters.")

        cleaned_text = response.text.strip().replace("```json", "").replace("```", "").strip()
        try:
            llm_output = json.loads(cleaned_text)
            offer_price = float(llm_output.get("price", 0.0))
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON response from Gemini: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Invalid response from valuation service.") from e

        db_product.initial_offer_price = offer_price
        db.add(db_product)
        db.commit()
        db.refresh(db_product)

    except ValueError as e:
        print(f"--- JSON PARSING FAILED ---")
        print(f"Original response text from Gemini: {response.text}")
        print(f"Error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to parse valuation response.")

    except Exception as e:
        print(f"--- GEMINI API CALL FAILED ---")
        print(f"Error: {e}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="The valuation service is currently unavailable.")

    return db_product


@router.post("/{product_id}/accept", response_model=schemas.ProductResponse)
def accept_offer(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    if db_product.status != "Registered":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This offer has already been actioned.")

    db_product.status = "Pending"
    db.commit()
    db.refresh(db_product)
    return db_product


@router.post("/{product_id}/decline", response_model=schemas.ProductResponse)
def decline_offer(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    if db_product.status != "Registered":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This offer has already been actioned.")

    db_product.status = "Closed"
    db.commit()
    db.refresh(db_product)
    return db_product


@router.post("/{product_id}/acquire", response_model=schemas.ProductResponse)
def acquire_product(product_id: int, db: Session = Depends(get_db)):
    try:
        db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
        if not db_product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        if db_product.status != "Pending":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product is not in a pending state and cannot be acquired.")
        db_product.status = "In Stock"
        db.commit()
        db.refresh(db_product)
        return db_product
    except Exception as e:
        logging.exception(f"Database error during product acquisition: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")