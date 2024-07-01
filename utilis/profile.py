import os
import random
import string
from typing import Optional
import jwt
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError
from fastapi import Depends, HTTPException, status
from database.db import DatabaseConnector
from models.token import TokenData
from config import config
import bcrypt
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
secret_key = config.Configurations.SECRET_KEY
algorithm = config.Configurations.ALGORITHM

user_db = DatabaseConnector("user")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        email: str = payload.get("email")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except PyJWTError:
        raise credentials_exception

    user = await user_db.get_user_by_email(email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    encoded_password = password.encode("utf-8")
    hashed = bcrypt.hashpw(encoded_password, salt)
    return hashed.decode("utf-8")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt

# def create_access_token(data: dict, expires_delta: timedelta):
#     to_encode = data.copy()
#     expire = datetime.utcnow() + expires_delta
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    encoded_plain_password = plain_password.encode("utf-8")
    return bcrypt.checkpw(encoded_plain_password, hashed_password.encode("utf-8"))

def generate_otp(length=6):
    digits = string.digits
    # return ''.join(random.choice(digits) for _ in range(length))
    return ''.join(random.choices(digits, k=length))

def send_email(to_email, otp):
    try:
        from_email = os.getenv("EMAIL")
        password = os.getenv("EMAIL_PASSWORD")

        subject = "Your OTP Code"
        body = f"Your OTP code is {otp}"

        msg = MIMEMultipart()
        msg["From"] = from_email
        msg["To"] = to_email
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(from_email, password)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def verify_password_reset(email: str, code: str) -> bool:
    return True
def verify_password_reset_settings(email: str) -> bool:
    return True