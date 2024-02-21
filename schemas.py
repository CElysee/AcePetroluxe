from datetime import datetime, time
from typing import Optional, List, Text

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    username: Optional[EmailStr] = None
    phone_number: str
    first_name: str
    last_name: str
    password: str
    gender: str
    country_id: Optional[int]
    is_active: Optional[bool] = None
    role: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    phone_number: str
    first_name: str
    last_name: str
    gender: str
    country_id: int
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    updated_at: datetime


class UserCheck(BaseModel):
    email: EmailStr


class UserId(BaseModel):
    id: int


class VendorCreate(BaseModel):
    vendor_name: str
    vendor_address: str
    vendor_contact_number: str
    vendor_email: str
    vendor_status: str
    vendor_country: int
    # vendor_logo: str
    created_at: Optional[datetime] = None


class VendorUpdate(BaseModel):
    vendor_name: Optional[str] = None
    vendor_address: Optional[str] = None
    vendor_contact_number: Optional[str] = None
    vendor_email: Optional[str] = None
    vendor_status: Optional[str] = None
    vendor_country: Optional[int] = None
    vendor_logo: Optional[str] = None
    updated_at: Optional[datetime] = None


class CustomerCreate(BaseModel):
    customer_first_name: str
    customer_last_name: str
    customer_email: str
    customer_phone_number: str
    customer_address: str
    customer_status: str
    customer_country: int
    created_at: Optional[datetime] = None


class CustomerUpdate(BaseModel):
    customer_first_name: Optional[str] = None
    customer_last_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone_number: Optional[str] = None
    customer_address: Optional[str] = None
    customer_status: Optional[str] = None
    customer_country: Optional[str] = None
    updated_at: Optional[datetime] = None