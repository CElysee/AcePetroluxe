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
from models import PurchaseOrder, PurchaseOrderItems, Vendors, Customer
from schemas import PurchaseOrderCreate
from sqlalchemy import func



router = APIRouter(
    tags=["Analytics"],
    prefix='/analytics'
)


@router.get("/general")
async def get_general_analytics(db: db_dependency):
    users = db.query(Customer).count()
    vendors = db.query(Vendors).count()
    customers = db.query(Customer).count()
    orders = db.query(PurchaseOrder).count()

    return {"users": users, "vendors": vendors, "customers": customers, "orders": orders}