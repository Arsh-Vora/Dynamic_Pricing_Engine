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
        prompt = f"Given a {product.device_model} in {product.condition} condition, that is {product.age_in_months} months old, what is a fair market price? Respond with only a JSON object containing a single key 'price' and its float value. Example: {{'price': 123.45}}"
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)

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