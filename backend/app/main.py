from fastapi import FastAPI
from .api import products
from .database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Recommerce Backend API",
    description="API for managing product registration and dynamic pricing.",
    version="0.1.0",
)

app.include_router(products.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to the Recommerce Backend API!"}
