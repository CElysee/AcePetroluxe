from datetime import datetime, timedelta
import calendar
import random
from typing import Annotated, Any, List
from sqlalchemy import select
from fastapi import APIRouter, HTTPException, Depends, UploadFile, Form, File
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from starlette import status

from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError

import models
import schemas
from database import SessionLocal
import logging
import os
import uuid
from dotenv import load_dotenv
from models import User
import smtplib
from email.message import EmailMessage
from jinja2 import Environment, FileSystemLoader
from email.mime.image import MIMEImage
import requests

router = APIRouter(
    tags=["Auth"],
    prefix='/auth'
)

load_dotenv()  # Load environment variables from .env

SECRET_KEY = 'a0ca9d98526e3a3d00cd899a53994e9a574fdecef9abe8bc233b1c262753cd2a'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token ')
logger = logging.getLogger(__name__)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


class UserResponse(BaseModel):
    id: int
    username: str
    # Add other fields as needed


def get_user_exception():
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return credentials_exception


def authenticated_user(username: str, password: str, db):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials", )
    if not bcrypt_context.verify(password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials", )
    return user


def create_access_token(username: str, user_id: int, expires_delta: timedelta, email: str, role: str):
    encode = {'sub': username, 'id': user_id, 'email': email, 'role': role}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def get_hashed_password(password: str):
    return bcrypt_context.hash(password)


def verify_password(plain_password, hashed_password):
    return bcrypt_context.verify(plain_password, hashed_password)


def get_user_by_email(email: str, password: str, db: Session):
    query = db.query(models.User).filter(models.User.email == email)
    user = query.first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials", )
    if not bcrypt_context.verify(password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password", )
    user.last_login = datetime.now()
    db.commit()
    return user


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)], db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_role: str = payload.get('role')
        user = db.query(models.User).filter(models.User.username == username).first()
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user.")
        # return {'username': username, 'id': user_id, 'user_role': user_role}
        return user

    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user.")


async def get_current_active_user(
        current_user: Annotated[schemas.UserOut, Depends(get_current_user)]
):
    return current_user


user_dependency = Annotated[dict, Depends(get_current_user)]


class Token(BaseModel):
    access_token: str
    token_type: str
    # role: str


class UserToken(BaseModel):
    access_token: str
    token_type: str
    role: str
    userId: int
    userData: dict


UPLOAD_FOLDER = "acePetroluxe"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def save_uploaded_file(file: UploadFile):
    file_extension = file.filename.split(".")[-1]
    random_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(UPLOAD_FOLDER, random_filename)
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    return random_filename


def read_email_template():
    template_path = os.path.join(os.getcwd(), "templates", "email", "email.html")
    with open(template_path, "r") as file:
        return file.read()


def send_sms(phone_number, message):
    url = 'https://api.mista.io/sms'
    api_key = os.getenv('386|hY4eAWqZdbXnMOccURnsvdkPF6myOZENEU7GPhOY ')
    sender_id = os.getenv('KIVUFEST')

    headers = {
        'x-api-key': api_key
    }
    payload = {
        'to': phone_number,
        'from': sender_id,
        'unicode': '0',
        'sms': message,
        'action': 'send-sms'
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        print(response)
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")


def generate_random_mixed():
    random_number = random.randint(10, 9999)
    return random_number


def get_user_by_id(user_id, db):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


def user_by_email(email, db):
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


def user_exist(email, db):
    user = db.query(models.User).filter(models.User.email == email).first()
    if user:
        return True
    else:
        return False


@router.get('/all', response_model=List[schemas.UserOut])
async def all_users(db: Session = Depends(get_db)):
    users = db.query(models.User).order_by(models.User.id.desc()).all()
    return users


@router.get("/usersCount")
async def get_users_count(db: Session = Depends(get_db)):
    count_users = db.query(models.User).count()
    count_users_active = db.query(models.User).filter(models.User.is_active == True).count()
    count_users_loggedin = db.query(models.User).filter(models.User.last_login != None).count()
    count_new_users = db.query(models.User).filter(
        models.User.created_at >= datetime.now() - timedelta(days=30)).count()
    return {"total_users": count_users, "active_users": count_users_active, "logged_in_users": count_users_loggedin,
            "new_users": count_new_users}


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_user(db: Session = Depends(get_db), user_request: schemas.UserCreate = Depends()):
    check_user = user_exist(user_request.email, db)
    if check_user:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Email already exist")
    try:
        hashed_password = get_hashed_password(user_request.password)
        new_user = models.User(
            first_name=user_request.first_name,
            last_name=user_request.last_name,
            phone_number=user_request.phone_number,
            email=user_request.email,
            username=user_request.email,
            gender=user_request.gender,
            role=user_request.role,
            is_active=True,
            country_id=user_request.country_id,
            password=hashed_password,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        db.add(new_user)
        db.commit()
        return {"message": "User created successfully"}

    except Exception as e:
        db.rollback()
        error_msg = f"Error adding a new user: {str(e)}"
        logger.exception(error_msg)
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=error_msg)


@router.post('/verify_phone_number')
async def verify_phone_number(phone_number: str, db: db_dependency):
    new_phone = "+250" + phone_number
    user = db.query(models.User).filter(models.User.phone_number == phone_number).first()
    if user:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Phone number already exist")
    else:
        return send_sms(new_phone, f"Your verification code is {generate_random_mixed}")
        # return {"message": "Verification code sent successfully"}


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticated_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user.")

    token = create_access_token(user.username, user.id, timedelta(minutes=60), user.email, user.role)

    return {'message': "Successfully Authenticated", 'access_token': token, 'token_type': 'bearer'}


@router.post("/login", response_model=UserToken)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    # user = authenticated_user(form_data.username, form_data.password, db)
    user = get_user_by_email(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    token = create_access_token(user.username, user.id, timedelta(minutes=60), user.email, user.role)
    user_info = {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "phone_number": user.phone_number,
        "username": user.username,
        "role": user.role,
    }
    return {'access_token': token, 'token_type': 'bearer', 'role': user.role, 'userId': user.id, 'userData': user_info}


# User info by id
@router.get("/{user_id}")
async def get_user(user_id: int, db: db_dependency):
    user = get_user_by_id(user_id, db)
    country = user.country
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    data = {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "phone_number": user.phone_number,
        "username": user.username,
        "role": user.role,
        "gender": user.gender,
        "country_id": user.country_id,
        "country": country,
        "is_active": user.is_active,
    }
    return data


@router.post("/check_username", status_code=status.HTTP_200_OK)
async def check_username(user_request: schemas.UserCheck, db: db_dependency):
    user = user_by_email(user_request.email, db)
    if user is None:
        return {'message': "Email not registered"}
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Account is not yet Approved")
    elif user:
        country_details = user.country
        details = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "country": country_details
        }
        return {"message": "Account is registered", "data": details}


@router.get("/users/me", response_model=schemas.UserOut)
async def get_me(current_user: dict = Depends(get_current_user)):
    return current_user


@router.put("/update", status_code=status.HTTP_200_OK)
async def update_profile(
        first_name: str = Form(None),
        last_name: str = Form(None),
        email: str = Form(None),
        phone_number: str = Form(None),
        gender: str = Form(None),
        user_id: str = Form(...),
        country_id: int = Form(None),
        is_active: bool = Form(None),
        db: Session = Depends(get_db),
):
    try:
        user = get_user_by_id(user_id, db)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        # Update user and user profile fields
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        if email:
            user.email = email
        if phone_number:
            user.phone_number = phone_number
        if is_active:
            user.is_active = is_active
        if country_id:
            user.country_id = country_id
        if gender:
            user.gender = gender  # Assuming you intended to update the country field

        # Commit the changes to the database
        db.commit()

        return {"message": "Profile updated successfully"}

    except Exception as e:
        db.rollback()  # Rollback the transaction in case of an exception
        # raise HTTPException(status_code=500, detail="Error updating user profile")
        return {"message": f"Error updating profile: {str(e)}"}

    finally:
        db.close()


@router.put("/users/update_password", status_code=status.HTTP_200_OK)
async def update_password(
        old_password: str = Form(...),
        new_password: str = Form(...),
        user_id: str = Form(...),
        db: Session = Depends(get_db),
):
    user = get_user_by_id(user_id, db)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if old_password and new_password:
        if not bcrypt_context.verify(old_password, user.password):
            raise HTTPException(status_code=400, detail="Old password is incorrect")
        else:
            user.password = get_hashed_password(new_password)
            # Commit the changes to the database
            db.commit()
            return {"message": "Password updated successfully"}
    else:
        raise HTTPException(status_code=400, detail="Old password is incorrect")


@router.delete("/delete")
async def delete_user(user_id: int, db: db_dependency):
    user = get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}