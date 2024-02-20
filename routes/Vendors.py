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
from models import Vendors
from schemas import VendorCreate, VendorUpdate

router = APIRouter(
    tags=["Vendor"],
    prefix="/vendor"
)


@router.get("/all")
async def list_all(db: db_dependency):
    vendor = db.query(Vendors).all()
    return vendor


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_vendor(vendor_request: VendorCreate, db: Session = Depends(get_db)):
    check_vendor = db.query(Vendors).filter(Vendors.vendor_name == vendor_request.vendor_name).first()
    if check_vendor:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Vendor already exists")

    vendor = Vendors(
        vendor_name=vendor_request.vendor_name,
        vendor_address=vendor_request.vendor_address,
        vendor_contact_number=vendor_request.vendor_contact_number,
        vendor_email=vendor_request.vendor_email,
        vendor_status=vendor_request.vendor_status,
        created_at=datetime.now()
    )
    db.add(vendor)
    db.commit()
    db.refresh(vendor)
    return {"message": "Vendor created successfully", "data": vendor}


@router.get("/{vendor_id}")
async def get_vendor(vendor_id: int, db: db_dependency):
    vendor = db.query(Vendors).filter(Vendors.id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor does not exist")
    return vendor


@router.put("/update")
async def update_vendor(vendor_id: int, vendor_request: VendorUpdate, db: Session = Depends(get_db)):
    vendor = db.query(Vendors).filter(Vendors.id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor does not exist")
    if vendor_request.vendor_name:
        vendor.vendor_name = vendor_request.vendor_name
    if vendor_request.vendor_address:
        vendor.vendor_address = vendor_request.vendor_address
    if vendor_request.vendor_contact_number:
        vendor.vendor_contact_number = vendor_request.vendor_contact_number
    if vendor_request.vendor_email:
        vendor.vendor_email = vendor_request.vendor_email
    if vendor_request.vendor_status:
        vendor.vendor_status = vendor_request.vendor_status
    vendor.updated_at = datetime.now()
    db.commit()
    db.refresh(vendor)
    return vendor


@router.delete("/delete")
async def delete_vendor(vendor_id: int, db: db_dependency):
    vendor = db.query(Vendors).filter(Vendors.id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor does not exist")
    db.delete(vendor)
    db.commit()
    return {"message": "Vendor deleted successfully"}
