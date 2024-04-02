from fastapi import HTTPException
from hashing import verify_hash
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from typing import Generator
from models import Email_User
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig


# Get the database URL from the environment variable
DATABASE_URL = os.environ.get("DATABASE_URL")

# Check if DATABASE_URL is defined
if DATABASE_URL is None:
    raise EnvironmentError("DATABASE_URL environment variable is not defined.")

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency to get the database session
def get_database() -> Generator[Session, None, None]:
    # Provide a database session to use within the request
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



def get_email_user(email: str):
    db = SessionLocal()
    try:
        email_user = db.query(Email_User).filter(Email_User.username == email).first()
        if not email_user:
            raise HTTPException(status_code=404, detail=f"Email_user not found with email '{email}'")
        return email_user
    except SQLAlchemyError as e:
        raise RuntimeError(f"Error retrieving email_user: {e}")
    finally:
        db.close()




def verify_email_user_password(plain_password: str, hashed_password: str) -> bool:
    # Verify the plain password against the hashed password using bcrypt
    return verify_hash(plain_password, hashed_password)




async def send_reset_password_email(email: str, token: str, origin: str):
    reset_url = f"{origin}/auth/reset-password?token={token}&email={email}"
    message = f"""
    <p>Please reset your password by clicking on the following link:</p>
    <p><a href="{reset_url}">Reset Password</a></p>
    """

    # Set up FastMail configurations
    conf = ConnectionConfig(
        MAIL_USERNAME="your_email@example.com",
        MAIL_PASSWORD="your_email_password",
        MAIL_FROM="noreply@example.com",
        MAIL_PORT=587,
        MAIL_SERVER="smtp.example.com",
        MAIL_TLS=True,
        MAIL_SSL=False,
        USE_CREDENTIALS=True
    )

    # Create FastMail instance
    fm = FastMail(conf)

    # Create MessageSchema for the email
    message_schema = MessageSchema(
        subject="Reset Password",
        recipients=[email],
        body=message,
        subtype="html"
    )

    # Send the email asynchronously
    await fm.send_message(message_schema)
