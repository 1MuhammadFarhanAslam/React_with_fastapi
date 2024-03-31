from fastapi import HTTPException, Depends, APIRouter, Header, Form, Request, status
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from google.oauth2 import id_token
from google.auth.transport import requests
import jwt
import os
from models import React_User, React_user_Token, Token, Email_User
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy import create_engine
from typing import Generator
from hashing import hash_password, verify_hash
from react_database import get_email_user, verify_email_user_password, send_reset_password_email
import secrets


router = APIRouter()

# Get the database URL from the environment variable
DATABASE_URL = os.environ.get("DATABASE_URL")
# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# SQLAlchemy models
Base = declarative_base()

def initialize_database():
    from models import Base
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully.")

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
GOOGLE_Email_LOGIN_SECRET_KEY = os.environ.get("GOOGLE_Email_LOGIN_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def React_JWT_Token(data: dict, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, GOOGLE_Email_LOGIN_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



@router.post("/api/google-signin", tags=["React"])
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
            # User already exists, return his/her details
            access_token_expires = timedelta(minutes=30)
            access_token = React_JWT_Token(data={"sub": existing_user.email}, expires_delta=access_token_expires)
            print(access_token)

            return {
                "message": "Log-in successfully! User already exists.",
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
                "message": "Sign-up successfully. User created successfully.",
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
    

@router.post("/api/email-signup", tags=["React"])
async def email_signup(request: Request, db: Session = Depends(get_database)):
    try:
        data = await request.json()
        email = data.get('email')
        password = data.get('password')

        # Check if the user already exists in the database
        existing_user = db.query(Email_User).filter(Email_User.email == email).first()

        if existing_user:
            print("messege: User already exists. Please sign in instead.")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists. Please sign in instead.")  
        
        else:
            # User does not exist, proceed with signup.
            hashed_password = hash_password(password)
            user = Email_User(email=email, password=hashed_password)
            db.add(user)
            db.commit()


            # Generate an access token for the new user
            access_token_expires = timedelta(minutes=30)
            access_token = React_JWT_Token(data={"sub": user.email}, expires_delta=access_token_expires)
            print("_______________access_token_______________", access_token)

            return {
                "message": "Signup successful! User created successfully.",
                "user_info": {
                    "id": user.id,
                    "created_at": user.created_at,
                    "email": user.email,
                    "status": user.status,
                    "role": user.role
                },
                "access_token": access_token,
                "token_type": "bearer"
            }
        
    except:
        raise HTTPException(status_code=400, detail="User already exists. Please sign in instead.")

    

@router.post("/api/email-signin", tags=["React"])
async def email_signin(request: Request, db: Session = Depends(get_database)):
    try:
        data = await request.json()
        email = data.get('email')
        password = data.get('password')

        # Retrieve the user from the database based on the email
        user = get_email_user(db, email)

        if not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found. Please sign up first.")
        
        else:
            # Verify the password
            if not verify_email_user_password(password, user.password):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect password.")

            # Generate an access token for the user
            access_token_expires = timedelta(minutes=30)
            access_token = React_JWT_Token(data={"sub": user.email}, expires_delta=access_token_expires)

            return {
                "message": "Login successful! User already exists.",
                "user_info": {
                    "id": user.id,
                    "created_at": user.created_at,
                    "email": user.email,
                    "status": user.status,
                    "role": user.role
                },
                "access_token": access_token,
                "token_type": "bearer"
            }
            
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error: " + str(e))
    


@router.get("/api/auth/user", response_model=None, tags=["React"])
async def combined_user_auth(
    authorization: str = Header(...),  # Get the access token from the Authorization header
    db: Session = Depends(get_database)
):
    try:
        # Extract the token from the Authorization header
        token = authorization.split(" ")[1]  # Assuming the header format is "Bearer <token>"
        
        # Decode and verify the JWT token
        decoded_token = jwt.decode(token, GOOGLE_Email_LOGIN_SECRET_KEY, algorithms=[ALGORITHM])
        print("________________decoded_token________________", decoded_token)
        email = decoded_token.get("sub")  # Assuming "sub" contains the email address
        
        # Query the database based on the email to get user data from React_User and Email_User
        react_user = db.query(React_User).filter(React_User.email == email).first()
        email_user = db.query(Email_User).filter(Email_User.email == email).first()
        print("_______________user details in jwt token (React_User)___________" , react_user)
        print("_______________user details in jwt token (Email_User)___________" , email_user)
        
        if react_user:
            user_data = {
                "id": str(react_user.id),
                "created_at": react_user.created_at,
                "username": react_user.username,
                "email": react_user.email,
                "picture": react_user.picture,
                "email_verified": react_user.email_verified,
                "role": react_user.role
            }
        elif email_user:
            user_data = {
                "id": email_user.id,
                "created_at": email_user.created_at,
                "email": email_user.email,
                "status": email_user.status,
                "role": email_user.role
            }
        else:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "message": "User details retrieved successfully",
            "userData": user_data
        }
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

@router.post("/api/forgot-password", tags=["React"])
async def forgot_password(request: Request, db: Session = Depends(get_database)):
    try:
        data = await request.json()
        print("_______________data_______________", data)
        email = data.get('email')
        print("_______________email_______________", email)

        user = db.query(Email_User).filter(Email_User.email == email).first()

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

        password_token = secrets.token_hex(35)
        user.password_token = hash_password(password_token)
        db.commit()

        origin = "http://localhost:3000/"
        await send_reset_password_email(user.email, password_token, origin)

        return {"msg": "Please check your email for the reset password link."}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error: " + str(e))
    
