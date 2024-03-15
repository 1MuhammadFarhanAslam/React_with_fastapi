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
def get_database() -> Generator[Session, None, None]:
    # Provide a database session to use within the request
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/read/{id}", response_model=None, tags=["React"])
async def read_react_user(
    id: str,
    db: Session = Depends(get_database)
):
    try:
        # Query the user based on the role
        user = db.query(React_User).filter(React_User.id == id).first()
        
        logger.info(f"Attempting to retrieve user with id: {id}")
        print("_____________________User_____________________" , user)
        
        if user:
            user_data = {
                "id": str(user.id),
                "created_at": user.created_at,
                "username": user.username,
                "email": user.email,
                "picture": user.picture,
                "email_verified": user.email_verified,
                "role": user.role,
            }

            return user_data
        else:
            logger.warning(f"No user found with id: {id}")
            raise HTTPException(status_code=404, detail="No user found")
    except ValueError:
        logger.warning(f"Invalid id: {id}")
        raise HTTPException(status_code=400, detail="Invalid role")
    except Exception as e:
        logger.error(f"Error during user retrieval: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")