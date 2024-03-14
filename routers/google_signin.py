from fastapi import FastAPI, HTTPException, Depends, APIRouter
from datetime import datetime, timedelta
from uuid import uuid4
from pydantic import BaseModel
from google.oauth2 import id_token
from google.auth.transport import requests
import jwt
import os
from models import React_User, React_user_Token
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine

router = APIRouter()
# Get the database URL from the environment variable
DATABASE_URL = os.environ.get("DATABASE_URL")
GOOGLE_LOGIN_SECRET_KEY = os.environ.get("GOOGLE_LOGIN_SECRET_KEY")
ALGORITHM = "HS256"

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# SQLAlchemy models
Base = declarative_base()

def React_JWT_Token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, GOOGLE_LOGIN_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/google-signin")
async def google_signin(token: React_user_Token, db: Session = Depends(get_db)):
    try:
        # Verify the Google ID token
        ticket = id_token.verify_oauth2_token(token.id_token, requests.Request(), "274409146209-qp9qp2au3k9bgghu8tb7urf2j7qal8e3.apps.googleusercontent.com")
        
        # Extract user information from the token's payload
        user_data = {
            "username": ticket.get("name"),
            "email": ticket.get("email"),
            "picture": ticket.get("picture"),
            "email_verified": ticket.get("email_verified"),
        }

        # Create a User instance with additional fields
        user = React_User(**user_data)

        # Add the user to the database
        db.add(user)
        db.commit()

        access_token_expires = timedelta(minutes=30)
        access_token = React_JWT_Token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )

        return {
            "message": "Login successful",
            "userData": user.dict(),
            "access_token": access_token,
            "token_type": "bearer"
        }
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Server Error")