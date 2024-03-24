from fastapi import HTTPException
from hashing import verify_hash
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from typing import Generator
from models import Email_User
from typing import Union, Optional
from fastapi import HTTPException , Depends


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


# Helper function to verify email user password
def verify_email_user_password(email: str, current_password: str) -> Email_User:
    db = SessionLocal()
    user = db.query(Email_User).filter(Email_User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_hash(current_password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect password")
    return user


def authenticate_email_user(email: str, password: str , db: Session = Depends(get_database)) -> Union[Email_User, None]:
    if password is None:
        return { "error": "Password is required" }
    
    try:
        email_user = db.query(Email_User).filter(Email_User.email == email).first()

        if not email_user:
            return {"error": "User not found"}

        if not verify_hash(password, email_user.password):
            return {"error": "Incorrect password"}

        return email_user
    
    except Exception as e:
        # Handle exceptions here
        pass  # Placeholder for exception handling logic

    return None  # Return None if authentication fails