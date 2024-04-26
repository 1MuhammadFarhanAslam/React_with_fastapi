from fastapi import FastAPI, HTTPException, Depends, Form, status
from pydantic import BaseModel
from typing import Optional
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import random
import string
from datetime import datetime, timedelta
from models import PasswordResetRequest, PasswordResetSubmit, Email_User
from fastapi import HTTPException, APIRouter, Request
import requests
from fastapi.responses import JSONResponse, StreamingResponse
import os
import jwt
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine
from typing import Generator
from datetime import timedelta, datetime, timezone
from hashing import hash_password

router = APIRouter()


# Get the database URL from the environment variable
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL is None:
    raise Exception("DATABASE_URL environment variable is not set")

# Get the database URL from the environment variable
PASSWORD_RESET_SECRET_KEY = os.environ.get("PASSWORD_RESET_SECRET_KEY")
if PASSWORD_RESET_SECRET_KEY is None:
    raise Exception("PASSWORD_RESET_SECRET_KEY environment variable is not set")

SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
if SENDGRID_API_KEY is None:
    raise Exception("SENDGRID_API_KEY environment variable is not set")

ALGORITHM = "HS256"
PASSWORD_RESET_TOKEN_EXPIRE_MINUTES = 15  # Change to 30 minutes

# nginx_url = "api.bittaudio.ai"
nginx_url = "api.bittaudio.ai"
    

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def initialize_database():
    from models import Base
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully.")

# Dependency to get the database session
def get_database() -> Generator[Session, None, None]:
    # Provide a database session to use within the request
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def Password_Reset_Access_Token(data: dict, expires_delta=timedelta(minutes=PASSWORD_RESET_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, PASSWORD_RESET_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Generate a random 6-digit code for token
def Password_Reset_Code_Generator():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

# Send password reset email using SendGrid API
def send_reset_email(recipient_email, Password_Reset_Code):
    message = Mail(
        from_email="farhanmehar422538@gmail.com",  # Replace with your email
        to_emails=recipient_email,
        subject="Password Reset Request",
        html_content=f"Your password reset token is: {Password_Reset_Code}"
    )
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        if response.status_code == 202:
            return response
        else:
            raise HTTPException(status_code=400, detail="Email failed to send.")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail= str(e))


# Endpoint for requesting password reset and sending email
@router.post("/password/reset/request")
def request_password_reset(request: PasswordResetRequest, db: Session = Depends(get_database)):
    try:
        # Check if user exists in database
        user = db.query(Email_User).filter(Email_User.email == request.email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # if user exists
        if user:
            # Generate a strong password reset code for verification
            password_reset_code = Password_Reset_Code_Generator()

            # Generate a password reset access token with expiry
            reset_access_token = Password_Reset_Access_Token(data={"sub": request.email})

            # Check if the access token is valid (not expired)
            token_expiry = jwt.decode(reset_access_token, PASSWORD_RESET_SECRET_KEY, algorithms=[ALGORITHM])['exp']
            if datetime.fromtimestamp(token_expiry) <= datetime.now(timezone.utc):
                raise HTTPException(status_code=400, detail="Password reset token has expired")

            # Update the user's database record with the reset token and code
            user.password_reset_code = password_reset_code
            user.reset_access_token = reset_access_token
            db.add(user)
            db.commit()
            db.refresh(user)

            # Send the password reset email with the code
            if send_reset_email(request.email, password_reset_code):
                return {"message": "Password reset email sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



# Endpoint for submitting password reset token and new password
@router.post("/password/reset/submit")
def submit_password_reset(request: PasswordResetSubmit, db: Session = Depends(get_database)):
    try:
        # Check if user exists in database
        user = db.query(Email_User).filter(Email_User.email == request.email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Check if password reset code matches database value
        if user.password_reset_code != request.reset_code:
            raise HTTPException(status_code=400, detail="Invalid password reset code")
        
        # Decode the JWT access token
        decoded_token = jwt.decode(user.reset_access_token, PASSWORD_RESET_SECRET_KEY, algorithms=[ALGORITHM])
        email = decoded_token.get("sub")

        # Convert the expiration time from timestamp to datetime aware of UTC timezone
        exp_timestamp = decoded_token["exp"]
        exp_datetime_utc = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)

        # Check if the access token is valid (not expired)
        if datetime.now(timezone.utc) >= exp_datetime_utc:
            raise HTTPException(status_code=400, detail="Password reset token has expired")

        # Check if access token email matches user email
        if user.email != email:
            raise HTTPException(status_code=400, detail="Invalid access token")
        

        # Update the user's password with the new password
        new_hashed_password = hash_password(request.new_password)
        user.password = new_hashed_password
        user.password_reset_code = None
        user.reset_access_token = None
        db.add(user)
        db.commit()
        return {"message": "Password reset successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail= str(e))

