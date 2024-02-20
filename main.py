from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette import status
from fastapi.staticfiles import StaticFiles
import os
from cachetools import TTLCache
import models
from database import engine, db_dependency
from routes import (Auth, Vendors, Customer)
from routes.Auth import get_current_user, user_dependency

app = FastAPI()

models.Base.metadata.create_all(bind=engine)
# app.mount("/FoodCategory", StaticFiles(directory="FoodCategory"), name="images")
# # Your cache instance, replace with your specific cache implementation
# cache = TTLCache(maxsize=100, ttl=600)  # TTLCache as an example, use your actual cache implementation


app.include_router(Auth.router)
app.include_router(Vendors.router)
app.include_router(Customer.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}

