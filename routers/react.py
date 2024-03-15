from fastapi import FastAPI, HTTPException, Depends, APIRouter
from datetime import datetime, timedelta
from uuid import uuid4
from pydantic import BaseModel
from google.oauth2 import id_token
from google.auth.transport import requests
import jwt
import os
from models import React_User, React_user_Token
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy import create_engine
from fastapi.middleware.cors import CORSMiddleware
from routers import admin, user, login
from typing import Generator
from fastapi.logger import logger
from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID

router = APIRouter()

# Get the database URL from the environment variable
DATABASE_URL = os.environ.get("DATABASE_URL")
# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# SQLAlchemy models
Base = declarative_base()

# Dependency to get the database session
def get_database():
    # Provide a database session to use within the request
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/read/{username}", response_model=None, tags=["React"])
async def read_react_user(
    username: str,
    db: Session = Depends(get_database)
):
    try:
        logger.info(f"Attempting to retrieve user with ID: {username}")
        
        # Query the user based on the UUID
        user = db.query(React_User).filter(React_User.username == username).first()
        print("_____________________User_____________________" , user)
        
        if user:
            logger.info(f"User found: {user}")
            
            # Customizing the response body
            user_data = {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "picture": user.picture,
                "email_verified": user.email_verified,
                "role": user.role,
                "created_at": user.created_at.strftime("%Y-%m-%dT%H:%M:%S.%f")
            }
            
            return user_data
        else:
            logger.warning(f"User not found with ID: {username}")
            raise HTTPException(status_code=404, detail="User not found")
    except ValueError:
        logger.warning(f"Invalid UUID format for user ID: {username}")
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    except Exception as e:
        logger.error(f"Error during user retrieval: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")