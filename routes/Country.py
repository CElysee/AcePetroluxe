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
from models import Country

router = APIRouter(
    tags=["Country"],
    prefix='/country'
)


@router.get("/all")
async def get_country(db: db_dependency):
    country = db.query(Country).all()
    return country
