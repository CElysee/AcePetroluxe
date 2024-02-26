import os
import uuid
from datetime import datetime, timedelta
import calendar
import random
from typing import Annotated, Any, List
from sqlalchemy import select
from fastapi import APIRouter, HTTPException, Depends, UploadFile, Form, File
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from starlette import status
from database import db_dependency, get_db
from UploadFile import FileHandler
from models import Customer
from schemas import CustomerCreate, CustomerUpdate

router = APIRouter(
    tags=["Customer"],
    prefix='/customer'
)


@router.get("/all")
async def get_vendors(db: db_dependency):
    vendors = db.query(Customer).all()
    return vendors


@router.get("/count")
async def customer_count(db: db_dependency):
    customer = db.query(Customer).count()
    active_customer = db.query(Customer).filter(Customer.customer_status == "Active").count()
    recently_added_customer = db.query(Customer).filter(
        Customer.created_at >= datetime.now() - timedelta(days=30)).count()
    return {"customer_count": customer, "active_customer": active_customer,
            "recently_added_customer": recently_added_customer}


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_customer(
        customer_request: CustomerCreate,
        db: Session = Depends(get_db)
):
    check_customer = db.query(Customer).filter(Customer.customer_email == customer_request.customer_email).first()
    if check_customer:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Customer already exists")

    customer = Customer(
        customer_first_name=customer_request.customer_first_name,
        customer_last_name=customer_request.customer_last_name,
        customer_email=customer_request.customer_email,
        customer_phone_number=customer_request.customer_phone_number,
        customer_status=customer_request.customer_status,
        customer_address=customer_request.customer_address,
        customer_country=customer_request.customer_country,
        created_at=datetime.now()
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return {"message": "Customer created successfully", "data": customer}


@router.get("/{customer_id}")
async def get_customer(customer_id: int, db: db_dependency):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer does not exist")
    return customer


@router.put("/update")
async def update_customer(customer_id: int, customer_request: CustomerUpdate, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer does not exist")

    if customer_request.customer_first_name:
        customer.customer_first_name = customer_request.customer_first_name
    if customer_request.customer_last_name:
        customer.customer_last_name = customer_request.customer_last_name
    if customer_request.customer_email:
        customer.customer_email = customer_request.customer_email
    if customer_request.customer_phone_number:
        customer.customer_phone_number = customer_request.customer_phone_number
    if customer_request.customer_status:
        customer.customer_status = customer_request.customer_status
    if customer_request.customer_address:
        customer.customer_address = customer_request.customer_address
    customer.updated_at = datetime.now()
    db.commit()
    db.refresh(customer)

    return {"message": "Customer updated successfully", "data": customer}


@router.delete("/delete")
async def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer does not exist")
    db.delete(customer)
    db.commit()
    return {"message": "Customer deleted successfully"}
