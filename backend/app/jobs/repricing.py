import os
import sys
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the parent directory to the sys.path to allow imports from app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models import Product

# Database setup (reusing from database.py for simplicity)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:secret@recommerce_db:5432/recommerce")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def run_repricing_job():
    db: Session = next(get_db())
    print("Starting repricing job...")

    try:
        # Fetch all 'In Stock' products
        in_stock_products = db.query(Product).filter(Product.status == 'In Stock').all()

        # Fetch all 'Sold' products within the last 30 days
        thirty_days_ago = datetime.now() - timedelta(days=30)
        sold_products_last_30_days = db.query(Product).filter(
            Product.status == 'Closed', # Assuming 'Closed' means sold for now, or add a 'Sold' status later
            Product.sold_at >= thirty_days_ago
        ).all()

        # Group products by device_model
        products_by_model = {}
        for product in in_stock_products:
            products_by_model.setdefault(product.device_model, {'in_stock': [], 'sold': []})['in_stock'].append(product)
        for product in sold_products_last_30_days:
            products_by_model.setdefault(product.device_model, {'in_stock': [], 'sold': []})['sold'].append(product)

        for device_model, data in products_by_model.items():
            stock_level = len(data['in_stock'])
            sales_velocity = len(data['sold'])

            # Apply Pricing Rules
            LOW_STOCK_THRESHOLD = 5
            HIGH_VELOCITY_THRESHOLD = 10
            
            price_adjustment_factor = 1.0 # Start with no change

            if stock_level < LOW_STOCK_THRESHOLD and sales_velocity > HIGH_VELOCITY_THRESHOLD:
                price_adjustment_factor = 1.10 # Increase price by 10%
            elif stock_level > (LOW_STOCK_THRESHOLD * 2):
                price_adjustment_factor = 0.95 # Decrease price by 5%
            
            print(f"Model: {device_model}, Stock: {stock_level}, Sales Velocity: {sales_velocity}, Adjustment Factor: {price_adjustment_factor}")

            # Apply this factor to all 'In Stock' items of this model
            for product in data['in_stock']:
                if product.current_market_price:
                    product.current_market_price *= price_adjustment_factor
                else: # First time pricing
                    product.current_market_price = product.initial_offer_price
                print(f"  - Product ID: {product.id}, New Market Price: {product.current_market_price:.2f}")

        db.commit()
        print("Repricing job completed successfully.")

    except Exception as e:
        db.rollback()
        print(f"Error during repricing job: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_repricing_job()
