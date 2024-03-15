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
from routers import admin, user, login, react
from typing import Generator
from fastapi.logger import logger
from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID
from admin_database import initialize_database, get_database


app = FastAPI()


# Allow CORS for all domains in this example
app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include routers
app.include_router(login.router, prefix="", tags=["Authentication"])
app.include_router(react.router, prefix="", tags=["React"])
app.include_router(admin.router, prefix="", tags=["Admin"])
app.include_router(user.router, prefix="", tags=["User"])

# Get the database URL from the environment variable
DATABASE_URL = os.environ.get("DATABASE_URL")
GOOGLE_LOGIN_SECRET_KEY = os.environ.get("GOOGLE_LOGIN_SECRET_KEY")
ALGORITHM = "HS256"

# # Create the SQLAlchemy engine
# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# # SQLAlchemy models
# Base = declarative_base()

def React_JWT_Token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, GOOGLE_LOGIN_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# def initialize_database():
#     Base.metadata.create_all(bind=engine)
#     print("Database initialized successfully.")

# # Dependency to get the database session
# def get_database() -> Generator[Session, None, None]:
#     # Provide a database session to use within the request
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

        
@app.post("/google-signin", tags=["React"])
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


# Main function to run the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port= 40337)


