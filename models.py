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