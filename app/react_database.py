from fastapi import HTTPException
from hashing import verify_hash
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from typing import Generator
from models import Email_User
import requests


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



def verify_email_user_password(plain_password: str, hashed_password: str):
    # Verify the plain password against the hashed password using bcrypt
    return verify_hash(plain_password, hashed_password)

        
def verify_email_user(email: str, password: str):
    db = SessionLocal()
    try:
        # Check if the email exists in the database
        email_user = db.query(Email_User).filter(Email_User.email == email).first()

        if not email_user:
            print("User not found as email does not exist. Please sign up first.")
            return HTTPException(status_code=404, detail="User not found as email does not exist. Please sign up first.")
        
        # Verify the password
        if email_user:
            if not verify_email_user_password(password, email_user.password):
                print("Ooops...........Incorrect password.")
                return HTTPException(status_code=401, detail="Ooops...........Incorrect password.")
            else:
                return email_user

    except SQLAlchemyError as e:
        raise RuntimeError(f"Error retrieving user: {e}")
    finally:
        db.close()

# def is_server_available(url: str):
#     try:
#         response = requests.get(url)
#         if response.status_code == 200:
#             return {"status": "Available", "detail": "Server is available."}
#         else:
#             return {"status": "Unavailable", "detail": "Server is temporarily Unavailable."}
#     except requests.exceptions.RequestException as e:
#         print(e)
#         return {"status": "Unavailable", "detail": "Server is temporarily Unavailable."}

# Define the function to check if the server is available (Please do not modify this function otherwise it can cause CORS issues and may be it will not perform correctly)
def is_server_available(url: str):
    try:
        response = requests.get(url, verify=False)  # Disable SSL verification
        if response.status_code == 200:
            # print("Server is available")
            return {"status": "Available", "detail": "Server is available."} 
        else:
            # print("Server is temporarily Unavailable")
            return {"status": "Unavailable", "detail": "Server is temporarily Unavailable."}
    except requests.exceptions.RequestException as e:
        print(e)
        return {"status": "Unavailable", "detail": "Server is temporarily Unavailable."}






