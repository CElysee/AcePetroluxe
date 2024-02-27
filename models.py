from datetime import time

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(50), unique=True, index=True)
    phone_number = Column(String(50), nullable=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    username = Column(String(50), unique=True, index=True)
    password = Column(String(250))
    gender = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True)
    country_id = Column(Integer, ForeignKey("countries.id"), nullable=True)
    role = Column(String(50), nullable=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    last_login = Column(DateTime)
    deleted = Column(Boolean)

    country = relationship("Country", back_populates="user")


class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    code = Column(String(50))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    user = relationship("User", back_populates="country")
    vendors = relationship("Vendors", back_populates="country")
    customers = relationship("Customer", back_populates="country")


class Vendors(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True)
    vendor_name = Column(String(50))
    vendor_address = Column(String(50))
    vendor_contact_number = Column(String(50))
    vendor_email = Column(String(50))
    vendor_status = Column(String(50))
    vendor_country = Column(Integer, ForeignKey("countries.id"))
    vendor_logo = Column(String(50))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    country = relationship("Country", back_populates="vendors")
    purchase_order = relationship("PurchaseOrder", back_populates="vendor")


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    customer_first_name = Column(String(50))
    customer_last_name = Column(String(50))
    customer_email = Column(String(50))
    customer_phone_number = Column(String(50))
    customer_address = Column(String(50))
    customer_status = Column(String(50))
    customer_country = Column(Integer, ForeignKey("countries.id"))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    country = relationship("Country", back_populates="customers")
    purchase_order = relationship("PurchaseOrder", back_populates="customer")


class PurchaseOrder(Base):
    __tablename__ = "purchase_order"

    id = Column(Integer, primary_key=True, index=True)
    po_number = Column(String(50))
    po_status = Column(String(50))
    po_vendor_id = Column(Integer, ForeignKey("vendors.id"))
    po_customer_id = Column(Integer, ForeignKey("customers.id"))
    po_additional_notes = Column(Text)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    vendor = relationship("Vendors", back_populates="purchase_order")
    customer = relationship("Customer", back_populates="purchase_order")
    purchase_order_items = relationship("PurchaseOrderItems", back_populates="purchase_order")


class PurchaseOrderItems(Base):
    __tablename__ = "purchase_order_items"

    id = Column(Integer, primary_key=True, index=True)
    po_id = Column(Integer, ForeignKey("purchase_order.id"))
    po_item_description = Column(Text)
    po_item_quantity = Column(Integer)
    po_item_unit_price = Column(Integer)
    po_item_total_price = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    purchase_order = relationship("PurchaseOrder", back_populates="purchase_order_items")
