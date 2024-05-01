from fastapi import APIRouter
from datetime import datetime, timedelta, timezone
import jwt
import os
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy import create_engine
from typing import Generator
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart



router = APIRouter()

# 

# Get the database URL from the environment variable
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL is None:
    raise Exception("DATABASE_URL environment variable is not set")

# Get the database URL from the environment variable
GOOGLE_EMAIL_LOGIN_SECRET_KEY = os.environ.get("GOOGLE_EMAIL_LOGIN_SECRET_KEY")
if GOOGLE_EMAIL_LOGIN_SECRET_KEY is None:
    raise Exception("GOOGLE_EMAIL_LOGIN_SECRET_KEY environment variable is not set")

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

VERIFICATION_SECRET_KEY = os.environ.get("VERIFICATION_SECRET_KEY")
if VERIFICATION_SECRET_KEY is None:
    raise Exception("VERIFICATION_SECRET_KEY environment variable is not set")

ALGORITHM = "HS256"
VERIFICATION_ACCESS_TOKEN_EXPIRE_DAYS = 36500  # Change to 30 minutes


# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# SQLAlchemy models
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


def Email_Verification_Code_Generator():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

def Verification_Token(data: dict, expires_delta=timedelta(days=VERIFICATION_ACCESS_TOKEN_EXPIRE_DAYS)):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=36500)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, VERIFICATION_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# def send_verification_email(recipient_email, verification_token):
#     # SMTP server configuration
#     smtp_server = SMTP_SERVER
#     smtp_port = 587  # Adjust as per your SMTP server settings
#     smtp_username = SMTP_USERNAME
#     smtp_password = SMTP_PASSWORD

#     # Verification link with token
#     verification_link = f"http://bittaudio.ai/verifyEmail?token={verification_token}"

#     # Email content with HTML formatting
#     sender_email = SENDER_EMAIL
#     subject = 'Email Verification'
#     body = f"""\
#     <!DOCTYPE html>
#     <html lang="en">

#     <head>
#         <meta charset="UTF-8">
#         <meta name="viewport" content="width=device-width, initial-scale=1.0">
#         <title>Email Verification</title>
#     </head>

#     <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">

#         <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 10px; padding: 20px; box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1);">
#             <h2 style="color: #333333; text-align: center;">Email Verification</h2>
#             <p style="color: #333333; font-size: 16px; line-height: 1.6;">Dear User,</p>
#             <p style="color: #333333; font-size: 16px; line-height: 1.6;">Thank you for signing up with us. To complete your registration and verify your email address, please click the button below:</p>
#             <div style="text-align: center; margin-top: 20px;">
#                 <a href="{verification_link}" style="background-color: #007bff; color: #ffffff; text-decoration: none; padding: 10px 20px; border-radius: 5px; font-weight: bold; display: inline-block;">Verify Email</a>
#             </div>
#             <p style="color: #333333; font-size: 16px; line-height: 1.6; margin-top: 20px;">Alternatively, you can copy and paste the following link into your browser:</p>
#             <p style="color: #333333; font-size: 16px; line-height: 1.6; margin-top: 10px;">{verification_link}</p>
#             <p style="color: #333333; font-size: 16px; line-height: 1.6; margin-top: 20px;">If you did not sign up for an account, please ignore this email.</p>
#             <p style="color: #333333; font-size: 16px; line-height: 1.6; margin-top: 20px;">Thank you,<br>Team YourAppName</p>
#         </div>

#     </body>

#     </html>

#     """

#     # Create the email message
#     message = MIMEMultipart()
#     message['From'] = sender_email
#     message['To'] = recipient_email
#     message['Subject'] = subject
#     message.attach(MIMEText(body, 'html'))

#     # Connect to the SMTP server
#     try:
#         server = smtplib.SMTP(smtp_server, smtp_port)
#         server.starttls()
#         server.login(smtp_username, smtp_password)

#         # Send email
#         server.sendmail(sender_email, recipient_email, message.as_string())
#         print('--------Email sent successfully----------')
#         return True  # Email sent successfully
#     except Exception as e:
#         print(f'-------Error sending email: {e}--------')
#         return False  # Email sending failed
#     finally:
#         server.quit()  # Close the connection



def send_verification_email(recipient_email, verification_token, verification_code):
    # SMTP server configuration
    smtp_server = SMTP_SERVER
    smtp_port = 587  # Adjust as per your SMTP server settings
    smtp_username = SMTP_USERNAME
    smtp_password = SMTP_PASSWORD

    # Website link
    website_link = "http://bittaudio.ai"

    # Verification link with token
    verification_link = f"http://bittaudio.ai/auth/verification?token={verification_token}"

    # Email content with HTML formatting
    sender_name = 'bittaudio.ai'
    sender_email = SENDER_EMAIL
    subject = 'Email Verification'
    body = f"""\
    <!DOCTYPE html>
    <html lang="en">

    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Email Verification</title>
    </head>

    <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">

        <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 10px; padding: 20px; box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1);">
            <h2 style="color: #333333; text-align: center;">Email Verification</h2>
            <p style="color: #333333; font-size: 16px; line-height: 1.6;">Dear User,</p>
            <p style="color: #333333; font-size: 16px; line-height: 1.6;">Thank you for signing up with us. Your email verification code is: <strong>{verification_code}</strong>. To complete your registration and verify your email address, please click the button below and enter your email verification code:</p>
            <div style="text-align: center; margin-top: 20px;">
                <a href="{verification_link}" style="background-color: #007bff; color: #ffffff; text-decoration: none; padding: 10px 20px; border-radius: 5px; font-weight: bold; display: inline-block;">Verify Email</a>
            </div>
            <p style="color: #333333; font-size: 16px; line-height: 1.6; margin-top: 20px;">If you did not sign up for an account, please disregard this email.</p>
            <p style="color: #333333; font-size: 16px; line-height: 1.6;">Thank you for choosing <strong><a href="{website_link}" style="color: #333333; text-decoration: none;">bittaudio.ai</a></strong>.</p>
            <p style="color: #333333; font-size: 16px; line-height: 1.6;">Best regards,<br><strong>Team bittaudio.ai</strong></p>
        </div>

    </body>

    </html>

    """

    # Create the email message
    message = MIMEMultipart()
    message['From'] = f"{sender_name} <{sender_email}>"
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
