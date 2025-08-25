from fastapi import FastAPI
from .api import products
from . import models       # <-- IMPORT YOUR MODELS FILE
from .database import engine # <-- IMPORT THE ENGINE

# This is the magic line that creates the tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Recommerce Backend API",
    description="API for managing product registration and dynamic pricing.",
    version="0.1.0",
)

app.include_router(products.router, prefix="/v1", tags=["Products"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Recommerce Backend API!"}
