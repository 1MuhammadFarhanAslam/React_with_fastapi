# from fastapi import APIRouter, HTTPException, Depends, Form
# import os
# import random
# import string
# from datetime import datetime, timedelta, timezone
# import jwt
# from sqlalchemy.orm import Session, sessionmaker
# from sqlalchemy import create_engine
# from typing import Generator
# from models import  PasswordResetSubmit, Email_User
# from hashing import hash_password
# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart


# router = APIRouter()

# # Get the database URL from the environment variable
# DATABASE_URL = os.environ.get("DATABASE_URL")
# if DATABASE_URL is None:
#     raise Exception("DATABASE_URL environment variable is not set")

# # Get the database URL from the environment variable
# PASSWORD_RESET_SECRET_KEY = os.environ.get("PASSWORD_RESET_SECRET_KEY")
# if PASSWORD_RESET_SECRET_KEY is None:
#     raise Exception("PASSWORD_RESET_SECRET_KEY environment variable is not set")

# SMTP_SERVER = os.environ.get("SMTP_SERVER")
# if SMTP_SERVER is None:
#     raise Exception("SMTP_SERVER environment variable is not set")

# SMTP_USERNAME = os.environ.get("SMTP_USERNAME")
# if SMTP_USERNAME is None:
#     raise Exception("SMTP_USERNAME environment variable is not set")

# SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
# if SENDER_EMAIL is None:
#     raise Exception("SENDER_EMAIL environment variable is not set")

# SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
# if SMTP_PASSWORD is None:
#     raise Exception("SMTP_PASSWORD environment variable is not set")

# ALGORITHM = "HS256"
# PASSWORD_RESET_TOKEN_EXPIRE_MINUTES = 15  # Change to 30 minutes

# # Create the SQLAlchemy engine
# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# # Dependency to get the database session
# def get_database() -> Generator[Session, None, None]:
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# def Password_Reset_Access_Token(data: dict, expires_delta=timedelta(minutes=PASSWORD_RESET_TOKEN_EXPIRE_MINUTES)):
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.now(timezone.utc) + expires_delta
#     else:
#         expire = datetime.now(timezone.utc) + timedelta(minutes=15)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, PASSWORD_RESET_SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt

# def Password_Reset_Code_Generator():
#     return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

# def Email_Verification_Code_Generator():
#     return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

# def send_reset_email(recipient_email, password_reset_code):
#     # SMTP server configuration
#     smtp_server = SMTP_SERVER
#     smtp_port = 587  # Adjust as per your SMTP server settings
#     smtp_username = SMTP_USERNAME
#     smtp_password = SMTP_PASSWORD

#     # Email content with HTML formatting
#     sender_email = SENDER_EMAIL
#     subject = 'Password Reset Email'
#     body = f"""\
#     <html>
#         <body>
#             <p style="font-size: larger;">The password reset code for your email is<strong> <span style="font-size: larger;">{password_reset_code}</span>.</strong> This code will expire in 15 minutes.</p>
#         </body>
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





# @router.post("/api/forgot-password")
# def request_password_reset(email: str = Form(...), db: Session = Depends(get_database)):
#     # Check if user exists in database
#     user = db.query(Email_User).filter(Email_User.email == email).first()
#     if not user:
#         print("--------User not found--------")
#         raise HTTPException(status_code=404, detail="User not found")
    
#     # Generate a strong password reset code for verification
#     password_reset_code = Password_Reset_Code_Generator()
#     print("--------Password reset code generated--------")

#     # Generate a password reset access token with expiry
#     reset_access_token = Password_Reset_Access_Token(data={"sub": email})
#     print("--------Password reset access token generated--------")

#     print(f"--------Password reset code------------: {password_reset_code}")
#     print(f"--------Password reset access token----------: {reset_access_token}")

#     # Send the password reset email with the code
#     if send_reset_email(email, password_reset_code):
#         # Update the user's database record with the reset token and code
#         user.password_reset_code = password_reset_code
#         user.reset_access_token = reset_access_token  # No need to decode
#         db.add(user)
#         db.commit()
#         db.refresh(user)
#         return {"message": "Password reset email sent successfully"}
#     else:
#         raise HTTPException(status_code=400, detail="Failed to send reset email")


# @router.post("/api/rest-password")
# def submit_password_reset(request: PasswordResetSubmit, db: Session = Depends(get_database)):
#     try:
#         # Check if user exists in database
#         user = db.query(Email_User).filter(Email_User.email == request.email).first()
#         if not user:
#             raise HTTPException(status_code=404, detail="User not found")

#         # Check if password reset code matches database value
#         if user.password_reset_code != request.reset_code:
#             raise HTTPException(status_code=400, detail="Invalid password reset code")
        
#         # Decode the JWT access token
#         decoded_token = jwt.decode(user.reset_access_token, PASSWORD_RESET_SECRET_KEY, algorithms=[ALGORITHM])

#         # Check if the access token is valid (not expired)
#         exp_timestamp = decoded_token["exp"]
#         exp_datetime_utc = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
#         if datetime.now(timezone.utc) >= exp_datetime_utc:
#             raise HTTPException(status_code=400, detail="Password reset token has expired. Generate new token by requesting a reset again.")

#         # Update the user's password with the new password
#         new_hashed_password = hash_password(request.new_password)
#         user.password = new_hashed_password
#         user.password_reset_code = None
#         user.reset_access_token = None
#         db.commit()
#         db.refresh(user)
#         return {"message": "Password reset successfully"}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))








# #--------------------------------------------------------------------------------------------------------------------------------------
# Workflow for forgot password with Rest link

from fastapi import APIRouter, HTTPException, Depends, Form, Request
import os
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


def send_reset_email(recipient_email, reset_access_token):
    # SMTP server configuration
    smtp_server = SMTP_SERVER
    smtp_port = 587  # Adjust as per your SMTP server settings
    smtp_username = SMTP_USERNAME
    smtp_password = SMTP_PASSWORD

    # Password reset link with token (assuming this is a frontend endpoint for reset)
    # reset_link = f"http://bittaudio.ai/auth/rest-password?token={reset_access_token}"
    reset_link = f"http://localhost:3000/auth/rest-password?token={reset_access_token}"

    # Email content with HTML formatting including a button
    sender_name = "bittaudio.ai"  # Update sender name
    sender_email = SENDER_EMAIL
    subject = 'Password Reset Email'
    body = f"""\
    <!DOCTYPE html>
    <html lang="en">

    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Password Reset Email</title>
    </head>

    <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">

        <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 10px; padding: 20px; box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1);">
            <h2 style="color: #333333; text-align: center;">Password Reset Email</h2>
            <p style="color: #333333; font-size: 16px; line-height: 1.6;">Dear User,</p>
            <p style="color: #333333; font-size: 16px; line-height: 1.6;">You have requested a password reset for your account. Please note that this request will expire in 15 minutes. To proceed with resetting your password, click the button below:</p>
            <div style="text-align: center; margin-top: 20px;">
                <a href="{reset_link}" style="background-color: #007bff; color: #ffffff; text-decoration: none; padding: 10px 20px; border-radius: 5px; font-weight: bold; display: inline-block;">Reset Password</a>
            </div>
            <p style="color: #333333; font-size: 16px; line-height: 1.6; margin-top: 20px;">If you did not request this password reset or have any concerns about your account's security, please contact our support team immediately.</p>
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
        raise HTTPException(status_code=400, detail="Failed to send reset email. Please try again later.")
    finally:
        server.quit()  # Close the connection


# Custom exception classes
class NoInputDataError(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="No input data provided")

class EmailNotFoundError(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Email not found")

class UserNotFoundError(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="User not found")

class FailedToSendResetEmailError(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Failed to send reset email. Please try again later.")

class TokenNotFoundError(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Token not found")

class PasswordNotFoundError(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Password not found")

class InvalidResetTokenError(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Invalid reset token")

class TokenExpiredError(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Token has expired. Send Forgot Password request again.")

class UpdatePasswordError(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Failed to update password")


# Your endpoint using custom exceptions
@router.post("/api/forgot-password")
async def request_password_reset(request: Request, db: Session = Depends(get_database)):
    try:
        request_data = await request.json()
        print('_______________request_data_____________', request_data)

        if not request_data:
            raise NoInputDataError()
        
        email = request_data.get("email")
        print("--------Email------------: ", email)
        if not email:
            raise EmailNotFoundError()
        
        # Check if user exists in database
        user = db.query(Email_User).filter(Email_User.email == email).first()
        if not user:
            print("--------User not found--------")
            raise UserNotFoundError()

        # Generate a password reset access token with expiry
        reset_access_token = Password_Reset_Access_Token(data={"sub": email})
        print("--------Password reset access token generated--------")
        print(f"--------Password reset access token----------: {reset_access_token}")

        try:
            send_reset_email(email, reset_access_token)
            print("--------Email sent successfully--------")
        except Exception as e:
            print(f"--------Error sending email: {e}--------")
            raise FailedToSendResetEmailError()

        # Update the user's database record with the reset token and code
        user.reset_access_token = reset_access_token  # No need to decode
        db.add(user)
        db.commit()
        db.refresh(user)
        db.close()
        return {"message": "Password reset email sent successfully"}

    except NoInputDataError as e:
        print(e)
        raise HTTPException(status_code=400, detail="No input data provided")
    except EmailNotFoundError as e:
        print(e)
        raise HTTPException(status_code=400, detail="Email not found")
    except UserNotFoundError as e:
        print(e)
        raise HTTPException(status_code=404, detail="User not found")
    except FailedToSendResetEmailError as e:
        print(e)
        raise HTTPException(status_code=400, detail="Failed to send reset email. Please try again later.")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal server error")


# Your endpoint using custom exceptions
@router.post("/api/reset-password")
async def submit_password_reset(request: Request, db: Session = Depends(get_database)):
    try:
        request_data = await request.json()
        print('_______________request_data_____________', request_data)

        token = request_data.get("token")
        print("Token: ", token)

        # Extract email from token
        decoded_token = jwt.decode(token, PASSWORD_RESET_SECRET_KEY, algorithms=[ALGORITHM])
        email: str = decoded_token.get("sub")
        print("Email: ", email)        

        new_password = request_data.get("confirmPassword")        
        print("Password: ", new_password)

        if not request_data:
            raise NoInputDataError()

        if not token:
            raise TokenNotFoundError()

        if not new_password:
            raise PasswordNotFoundError()

        # Check if user exists in database
        user = db.query(Email_User).filter(Email_User.email == email).first()
        if not user:
            raise UserNotFoundError()
        
        # Check if the saved reset token matches the incoming token
        if user.reset_access_token != token:
            raise InvalidResetTokenError()

        # Decode the JWT access token
        decoded_token = jwt.decode(token, PASSWORD_RESET_SECRET_KEY, algorithms=[ALGORITHM])

        # Check if the access token is valid (not expired)
        exp_timestamp = decoded_token["exp"]
        exp_datetime_utc = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
        if datetime.now(timezone.utc) >= exp_datetime_utc:
            raise TokenExpiredError()
        
        try:  
            # Update the user's password with the new password
            new_hashed_password = hash_password(new_password)
            user.password = new_hashed_password
            user.reset_access_token = None
            db.commit()
            db.refresh(user)
            db.close()
            return {"message": "Password reset successfully"}
        except Exception as e:
            print(f"{e}")
            raise UpdatePasswordError()

    except NoInputDataError as e:
        print(e)
        raise HTTPException(status_code=400, detail="No input data provided")
    except TokenNotFoundError as e:
        print(e)
        raise HTTPException(status_code=400, detail="Token not found")
    except PasswordNotFoundError as e:
        print(e)
        raise HTTPException(status_code=400, detail="Password not found")
    except UserNotFoundError as e:
        print(e)
        raise HTTPException(status_code=404, detail="User not found")
    except InvalidResetTokenError as e:
        print(e)
        raise HTTPException(status_code=400, detail="Invalid reset token")
    except TokenExpiredError as e:
        print(e)
        raise HTTPException(status_code=400, detail="Token has expired. Send Forgot Password request again.")
    except UpdatePasswordError as e:
        print(e)
        raise HTTPException(status_code=400, detail="Failed to update password")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail= "Internal server error")










#--------------------------------------------------------------------------------------------------------------------------------------

