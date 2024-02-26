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
    tags=["PurchaseOrder"],
    prefix='/purchaseOrder'
)


@router.get("/all")
async def get_purchase_order(db: db_dependency):
    purchase_order = db.query(PurchaseOrder).all()
    orders = []
    for order in purchase_order:
        vendor = db.query(Vendors).filter(Vendors.id == order.po_vendor_id).first()
        customer = db.query(Customer).filter(Customer.id == order.po_customer_id).first()
        items = db.query(PurchaseOrderItems).filter(PurchaseOrderItems.po_id == order.id).all()
        orders.append({"order": order, "vendor": vendor, "customer": customer, "items": items})
    return orders


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_purchase_order(
        purchase_order_request: PurchaseOrderCreate, db: db_dependency):
    check_purchase_order = db.query(PurchaseOrder).filter(
        PurchaseOrder.po_number == purchase_order_request.po_number).first()
    order_number = 0
    if check_purchase_order is None:
        order_number += 1
    else:
        order_number = int(check_purchase_order.po_number) + 1

    purchase_order = PurchaseOrder(
        po_vendor_id=purchase_order_request.po_vendor_id,
        po_customer_id=purchase_order_request.po_customer_id,
        po_status=purchase_order_request.po_status,
        po_number=str(order_number),  # Convert order_number to string here
        created_at=datetime.now()
    )
    db.add(purchase_order)
    db.commit()
    db.refresh(purchase_order)

    for item in purchase_order_request.itemList:
        purchase_order_item = PurchaseOrderItems(
            po_id=purchase_order.id,
            po_item_description=item.po_item_description,
            po_item_quantity=item.po_item_quantity,
            po_item_unit_price=item.po_item_unit_price,
            po_item_total_price=item.po_item_total_price,
            created_at=datetime.now()
        )
        db.add(purchase_order_item)
        db.commit()
        db.refresh(purchase_order_item)

    return {"message": "Purchase Order Created Successfully"}


@router.get("/order_id")
async def update_purchase_order(id: int, db: db_dependency):
    purchase_order = db.query(PurchaseOrder).filter(PurchaseOrder.id == id).first()
    if purchase_order is None:
        raise HTTPException(status_code=404, detail="Purchase Order not found")

    orders = []
    vendor = db.query(Vendors).filter(Vendors.id == purchase_order.po_vendor_id).first()
    customer = db.query(Customer).filter(Customer.id == purchase_order.po_customer_id).first()
    items = db.query(PurchaseOrderItems).filter(PurchaseOrderItems.po_id == purchase_order.id).all()
    orders.append({"order": purchase_order, "vendor": vendor, "customer": customer, "items": items})
    return orders


@router.get("/item_list")
async def get_item_list(order_id: int, db: db_dependency):
    items = db.query(PurchaseOrderItems).filter(PurchaseOrderItems.id == order_id).all()
    item_quantity_total = (
        db.query(func.sum(PurchaseOrderItems.po_item_quantity))
        .filter(PurchaseOrderItems.id == order_id)
        .scalar()  # Use .scalar() to retrieve the result directly
    )
    item_total_price = (
        db.query(func.sum(PurchaseOrderItems.po_item_total_price))
        .filter(PurchaseOrderItems.id == order_id)
        .scalar()  # Use .scalar() to retrieve the result directly
    )
    return {"items": items, "item_quantity_total": item_quantity_total, "item_total_price": item_total_price}


@router.get("/count")
async def get_purchase_order_count(db: db_dependency):
    purchase_order = db.query(PurchaseOrder).count()
    approved_orders = db.query(PurchaseOrder).filter(PurchaseOrder.po_status == "Approved").count()
    pending_orders = db.query(PurchaseOrder).filter(PurchaseOrder.po_status == "Pending").count()
    cancelled_orders = db.query(PurchaseOrder).filter(PurchaseOrder.po_status == "Cancelled").count()
    return {"purchase_order": purchase_order, "approved_orders": approved_orders, "pending_orders": pending_orders,
            "cancelled_orders": cancelled_orders}


@router.delete("/delete")
async def delete_purchase_order(id: int, db: db_dependency):
    purchase_order = db.query(PurchaseOrder).filter(PurchaseOrder.id == id).first()
    if purchase_order is None:
        raise HTTPException(status_code=404, detail="Purchase Order not found")
    db.delete(purchase_order)
    db.commit()
    return {"message": "Purchase Order Deleted Successfully"}
