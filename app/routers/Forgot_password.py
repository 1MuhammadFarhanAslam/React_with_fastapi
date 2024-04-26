from fastapi import FastAPI, APIRouter, HTTPException, Depends, Form
from typing import Optional
import os
import sendgrid
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
import random
import string
from datetime import datetime, timedelta, timezone
import jwt
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from typing import Generator
from models import PasswordResetRequest, PasswordResetSubmit, Email_User
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

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get the database session
def get_database() -> Generator[Session, None, None]:
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

def Password_Reset_Code_Generator():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

def send_reset_email(recipient_email, Password_Reset_Code):
    sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
    from_email = Email("zaiddev60gb@gmail.com")  # Change to your verified sender
    to_email = To(f"{recipient_email}")  # Change to your recipient
    subject = "Password Reset Request"
    content = Content("text/plain", f"Your password reset token is: {Password_Reset_Code}")  # Provide content type and content
    mail = Mail(from_email, to_email, subject, content)

    # Get a JSON-ready representation of the Mail object
    mail_json = mail.get()

    # Send an HTTP POST request to /mail/send
    response = sg.client.mail.send.post(request_body=mail_json)
    print(response.status_code)
    print(response.headers)
    if response.status_code == 200:
        return {"message": "Email sent successfully"}
    else:
        return {"message": "Email failed to send"}

@router.post("/password/reset_request")
def request_password_reset(email: str = Form(...), db: Session = Depends(get_database)):
    # Check if user exists in database
    user = db.query(Email_User).filter(Email_User.email == email).first()
    if not user:
        print("--------User not found--------")
        raise HTTPException(status_code=404, detail="User not found")
    
    # Generate a strong password reset code for verification
    password_reset_code = Password_Reset_Code_Generator()
    print("--------Password reset code generated--------")

    # Generate a password reset access token with expiry
    reset_access_token = Password_Reset_Access_Token(data={"sub": email})
    print("--------Password reset access token generated--------")

    print(f"--------Password reset code------------: {password_reset_code}")
    print(f"--------Password reset access token----------: {reset_access_token}")

    # Send the password reset email with the code
    if send_reset_email(email, password_reset_code):
        # Update the user's database record with the reset token and code
        user.password_reset_code = password_reset_code
        user.reset_access_token = reset_access_token.decode()  # Decode the bytes to string
        db.add(user)
        db.commit()
        db.refresh(user)
        return {"message": "Password reset email sent successfully"}
    else:
        raise HTTPException(status_code=400, detail="Failed to send reset email")

@router.post("/password/reset_submit")
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

        # Check if the access token is valid (not expired)
        exp_timestamp = decoded_token["exp"]
        exp_datetime_utc = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
        if datetime.now(timezone.utc) >= exp_datetime_utc:
            raise HTTPException(status_code=400, detail="Password reset token has expired")

        # Update the user's password with the new password
        new_hashed_password = hash_password(request.new_password)
        user.password = new_hashed_password
        user.password_reset_code = None
        user.reset_access_token = None
        db.commit()
        return {"message": "Password reset successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
