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
from models import  PasswordResetSubmit, Email_User
from hashing import hash_password
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


router = APIRouter()

# Get the database URL from the environment variable
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL is None:
    raise Exception("DATABASE_URL environment variable is not set")

# Get the database URL from the environment variable
PASSWORD_RESET_SECRET_KEY = os.environ.get("PASSWORD_RESET_SECRET_KEY")
if PASSWORD_RESET_SECRET_KEY is None:
    raise Exception("PASSWORD_RESET_SECRET_KEY environment variable is not set")

SMTP_SERVER = os.environ.get("SMTP_SERVER")
if SMTP_SERVER is None:
    raise Exception("SMTP_SERVER environment variable is not set")

SMTP_USERNAME = os.environ.get("SMTP_USERNAME")
if SMTP_USERNAME is None:
    raise Exception("SMTP_USERNAME environment variable is not set")

SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
if SENDER_EMAIL is None:
    raise Exception("SENDER_EMAIL environment variable is not set")

SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
if SMTP_PASSWORD is None:
    raise Exception("SMTP_PASSWORD environment variable is not set")

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

def send_reset_email(recipient_email, password_reset_code):
    # SMTP server configuration
    smtp_server = SMTP_SERVER
    smtp_port = 587  # Adjust as per your SMTP server settings
    smtp_username = SMTP_USERNAME
    smtp_password = SMTP_PASSWORD

    # Email content with HTML formatting
    sender_email = SENDER_EMAIL
    subject = 'Password Reset Email'
    body = f"""\
    <html>
        <body>
            <p style="font-size: larger;">The password reset code for your account is<strong> <span style="font-size: larger;">{password_reset_code}</span>.</strong>This code will expire in 15 minutes.</p>
        </body>
    </html>
    """

    # Create the email message
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = subject
    message.attach(MIMEText(body, 'html'))

    # Connect to the SMTP server
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)

        # Send email
        server.sendmail(sender_email, recipient_email, message.as_string())
        print('--------Email sent successfully----------')
        return True  # Email sent successfully
    except Exception as e:
        print(f'-------Error sending email: {e}--------')
        return False  # Email sending failed
    finally:
        server.quit()  # Close the connection



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
        user.reset_access_token = reset_access_token  # No need to decode
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
            raise HTTPException(status_code=400, detail="Password reset token has expired. Generate new token by requesting a reset again.")

        # Update the user's password with the new password
        new_hashed_password = hash_password(request.new_password)
        user.password = new_hashed_password
        user.password_reset_code = None
        user.reset_access_token = None
        db.commit()
        db.refresh(user)
        return {"message": "Password reset successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))








