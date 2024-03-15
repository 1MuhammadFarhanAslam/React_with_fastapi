from fastapi import HTTPException, Depends, APIRouter, Header
from datetime import datetime, timedelta
from uuid import uuid4
from google.oauth2 import id_token
from google.auth.transport import requests
import jwt
import os
from models import React_User, React_user_Token
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy import create_engine
from typing import Generator
from fastapi.logger import logger
from jose import jwt, JWTError
from typing import Optional

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

# Get the database URL from the environment variable
DATABASE_URL = os.environ.get("DATABASE_URL")
GOOGLE_LOGIN_SECRET_KEY = os.environ.get("GOOGLE_LOGIN_SECRET_KEY")
ALGORITHM = "HS256"

def React_JWT_Token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, GOOGLE_LOGIN_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



@router.post("/google-signin", tags=["React"])
async def google_signin(token: React_user_Token, db: Session = Depends(get_database)):
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

        # Check if the user already exists in the database
        existing_user = db.query(React_User).filter(React_User.email == user_data["email"]).first()

        if existing_user:
            # User already exists, return their details
            access_token_expires = timedelta(minutes=30)
            access_token = React_JWT_Token(data={"sub": existing_user.email}, expires_delta=access_token_expires)
            print(access_token)

            return {
                "message": "User already exists",
                "userData": {
                    "id": str(existing_user.id),
                    "username": existing_user.username,
                    "email": existing_user.email,
                    "picture": existing_user.picture,
                    "email_verified": existing_user.email_verified,
                    "role": existing_user.role
                },
                "access_token": access_token,
                "token_type": "bearer"
            }
        else:
            # User does not exist, create a new user and save it to the database
            user = React_User(**user_data)
            db.add(user)
            db.commit()

            access_token_expires = timedelta(minutes=30)
            access_token = React_JWT_Token(data={"sub": user.email}, expires_delta=access_token_expires)
            print(access_token)

            return {
                "message": "Login successful",
                "userData": {
                    "id": str(user.id),
                    "username": user.username,
                    "email": user.email,
                    "picture": user.picture,
                    "email_verified": user.email_verified,
                    "role": user.role
                },
                "access_token": access_token,
                "token_type": "bearer"
            }
    
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Server Error")
    


@router.get("/decode-token", response_model=None, tags=["React"])
async def decode_access_token(access_token: str, db: Session = Depends(get_database)):
    try:
        decoded_token = jwt.decode(access_token, GOOGLE_LOGIN_SECRET_KEY, algorithms=[ALGORITHM])
        email = decoded_token.get("sub")  # Assuming "sub" contains the email address
        
        # Query the database based on the email to get user data
        user = db.query(React_User).filter(React_User.email == email).first()
        print("_______________user details in jwt token___________" ,user)
        
        if user:
            return {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                # Add other user data fields as needed
            }
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

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