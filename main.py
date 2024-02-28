from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette import status
from fastapi.staticfiles import StaticFiles
import os
from cachetools import TTLCache
import models
from database import engine, db_dependency
from routes import (Auth, Vendors, Customer, Country, PurchaseOrder, Analytics)
from routes.Auth import get_current_user, user_dependency

app = FastAPI()

models.Base.metadata.create_all(bind=engine)
# app.mount("/FoodCategory", StaticFiles(directory="FoodCategory"), name="images")
# # Your cache instance, replace with your specific cache implementation
# cache = TTLCache(maxsize=100, ttl=600)  # TTLCache as an example, use your actual cache implementation

app.add_middleware(
    CORSMiddleware,
    # allow_origins=origins,
    allow_origins=["http://localhost:5173", "http://137.184.41.141:9000", "http://137.184.41.141:9001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(Auth.router)
app.include_router(Country.router)
app.include_router(Vendors.router)
app.include_router(Customer.router)
app.include_router(PurchaseOrder.router)
app.include_router(Analytics.router)

app.mount("/vendorLogo", StaticFiles(directory="vendorLogo"), name="images")
# Your cache instance, replace with your specific cache implementation
cache = TTLCache(maxsize=100, ttl=600)  # TTLCache as an example, use your actual cache implementation

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/vendorLogo/{filename}")
async def get_image(filename: str):
    """Get an image by filename."""
    if not os.path.exists(f"./vendorLogo/{filename}"):
        raise HTTPException(status_code=404, detail="Image not found")

    with open(f"./vendorLogo/{filename}", "rb") as f:
        image_data = f.read()

    return image_data
