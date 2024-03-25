from pydantic import EmailStr
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
import asyncio

async def send_reset_password_email(name: str, email: EmailStr, token: str, origin: str):
    reset_url = f"{origin}/auth/reset-password?token={token}&email={email}"
    message = f"""
    <p>Please reset your password by clicking on the following link:</p>
    <p><a href="{reset_url}">Reset Password</a></p>
    """

    # Set up FastMail configurations
    conf = ConnectionConfig(
        MAIL_USERNAME="your_email@example.com",
        MAIL_PASSWORD="your_email_password",
        MAIL_FROM="your_email@example.com",
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
