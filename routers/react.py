from fastapi import HTTPException, Depends, APIRouter, Header, Form, Request
from datetime import datetime, timedelta
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
import re

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
    React_User.metadata.create_all(bind=engine)
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
GOOGLE_LOGIN_SECRET_KEY = os.environ.get("GOOGLE_LOGIN_SECRET_KEY")
ALGORITHM = "HS256"


def React_JWT_Token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, GOOGLE_LOGIN_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



@router.post("/react/google-signin", tags=["React"])
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
    

@router.get("/react/auth/user", response_model=None, tags=["React"])
async def user_auth(
    authorization: str = Header(...),  # Get the access token from the Authorization header
    db: Session = Depends(get_database)
):
    try:
        # Extract the token from the Authorization header
        token = authorization.split(" ")[1]  # Assuming the header format is "Bearer <token>"
        
        # Decode and verify the JWT token
        decoded_token = jwt.decode(token, GOOGLE_LOGIN_SECRET_KEY, algorithms=[ALGORITHM])
        print("________________decoded_token________________", decoded_token)
        email = decoded_token.get("sub")  # Assuming "sub" contains the email address
        
        # Query the database based on the email to get user data
        user = db.query(React_User).filter(React_User.email == email).first()
        print("_______________user details in jwt token___________" ,user)
        
        if user:
            return {
                "message": "User details retrieved successfully",
                "userData": {
                    "id": str(user.id),
                    "created_at": user.created_at,
                    "username": user.username,
                    "email": user.email,
                    "picture": user.picture,
                    "email_verified": user.email_verified,
                    "role": user.role
                }
            }
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
    

# @router.get("/react/read/{id}", response_model=None, tags=["React"])
# async def read_react_user(
#     id: str,
#     authorization: str = Header(...),
#     db: Session = Depends(get_database)
# ):
#     try:
#         # Verify the authorization token here if needed

#         # Query the user based on the ID
#         user = db.query(React_User).filter(React_User.id == id).first()
        
#         logger.info(f"Attempting to retrieve user with id: {id}")
#         print("_____________________User_____________________" , user)
        
#         if user:
#             user_data = {
#                 "id": str(user.id),
#                 "created_at": user.created_at,
#                 "username": user.username,
#                 "email": user.email,
#                 "picture": user.picture,
#                 "email_verified": user.email_verified,
#                 "role": user.role,
#             }

#             return user_data
#         else:
#             logger.warning(f"No user found with id: {id}")
#             raise HTTPException(status_code=404, detail="No user found")
#     except ValueError:
#         logger.warning(f"Invalid id: {id}")
#         raise HTTPException(status_code=400, detail="Invalid role")
#     except Exception as e:
#         logger.error(f"Error during user retrieval: {e}")
#         raise HTTPException(status_code=500, detail="Internal Server Error")
    

# def expire_token(token: str):
#     # Invalidation logic: Set expiration to a past date
#     expired_token = token
#     expired_token["exp"] = datetime.utcnow() - timedelta(days=1)
#     return expired_token

# @router.get("/react/signout", tags=["React"])
# async def logout_user(authorization: str = Header(...)):
#     try:
#         # Extract the token from the Authorization header
#         token = authorization  # Assuming the header format is "Bearer <token>"
#         print("__________token__________:", token)
        
#         # Decode and verify the JWT token
#         decoded_token = jwt.decode(token, GOOGLE_LOGIN_SECRET_KEY, algorithms=[ALGORITHM])
#         print("________________decoded_token________________", decoded_token)

#         # Invalidate the token by setting its expiration to a past date
#         expired_token = expire_token(token)

#         return {"message": "Logout successful", "token": expired_token}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail="Internal Server Error")
    


# @router.post("/react/email-signin", tags=["React"])
# async def email_signin(email: str = Form(...), password: str = Form(..., min_length=8, max_length=16, regex="^[a-zA-Z0-9!@#$%^&*()_+{}\[\]:;<>,.?/~\\-=|\\\\]+$") , db: Session = Depends(get_database)):
#     try:

#         # Validate that both username and password are provided
#         if not email or not password:
#             raise HTTPException(status_code=400, detail="Both username and password are required.")

#         # Check if the user already exists in the database
#         existing_user = db.query(Email_User).filter(Email_User.email == email).first()
#         print("_______________existing_user_______________", existing_user)

#         if existing_user:
#             raise HTTPException(status_code=400, detail="Email already exists. Try with another email.")

#         if not re.match("^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+$", password):
#             raise HTTPException(status_code=400, detail="Password must contain at least one uppercase letter, one lowercase letter, one digit, and one special character.")

#         # User already exists
#         if existing_user.email == email and verify_hash(existing_user.password, password):

#             # Generate an access token for the new user and return his/her details
#             access_token_expires = timedelta(minutes=30)
#             access_token = React_JWT_Token(data={"sub": user.email}, expires_delta=access_token_expires)
#             print("_______________access_token_______________", access_token)

#             return {
#                 "message": "Log-in successfully! User already exists.",
#                 "user_info" : {
#                     "id": str(existing_user.id),
#                     "created_at": existing_user.created_at,
#                     "username": existing_user.username,
#                     "email": existing_user.email,
#                     "password": existing_user.password,
#                     "status": existing_user.status,
#                     "role": existing_user.role
#                 },
#                 "access_token": access_token,
#                 "token_type": "bearer"
#             }

#         else:
#             # User does not exist, hash the password and save the user to the database
#             hashed_password = hash_password(password)

#             # Create a new user and save it to the database
#             user = Email_User(email=email, hashed_password=hashed_password)
#             db.add(user)
#             db.commit()

#             access_token_expires = timedelta(minutes=30)
#             access_token = React_JWT_Token(data={"sub": user.email}, expires_delta=access_token_expires)
#             print("_______________access_token_______________", access_token)


#             return {
#                 "message": "Sign-up successfully! User created successfully.",
#                 "user_info" : {
#                     "id": str(user.id),
#                     "created_at": user.created_at,
#                     "username": user.username,
#                     "email": user.email,
#                     "password": user.password,
#                     "status": user.status,
#                     "role": user.role
#                 },
#                 "access_token": access_token,
#                 "token_type": "bearer"
#             }

#     except Exception as e:
#         print(e)
#         raise HTTPException(status_code=500, detail="Server Error")


@router.post("/react/email-signin", tags=["React"])
async def email_signin(request: Request, db: Session = Depends(get_database)):
    try:

        form_data = await request.form()
        print("______________form_data______________", form_data)
        email = form_data.get('email')
        password = form_data.get('password')
        # Check if the user already exists in the database
        existing_user = db.query(Email_User).filter(Email_User.email == email).first()

        if existing_user:
            # User exists, check password for login
            if verify_hash(existing_user.password, password):
                # Generate an access token for the user
                access_token_expires = timedelta(minutes=30)
                access_token = React_JWT_Token(data={"sub": existing_user.email}, expires_delta=access_token_expires)

                return {
                    "message": "Login successful!",
                    "user_info": {
                        "id": str(existing_user.id),
                        "created_at": existing_user.created_at,
                        "username": existing_user.username,
                        "email": existing_user.email,
                        "status": existing_user.status,
                        "role": existing_user.role
                    },
                    "access_token": access_token,
                    "token_type": "bearer"
                }
            else:
                raise HTTPException(status_code=401, detail="Incorrect password.")

        else:
            # User does not exist, hash the password and save the user to the database for signup
            hashed_password = hash_password(password)
            user = Email_User(email=email, password=hashed_password)
            db.add(user)
            db.commit()

            # Generate an access token for the new user
            access_token_expires = timedelta(minutes=30)
            access_token = React_JWT_Token(data={"sub": user.email}, expires_delta=access_token_expires)

            return {
                "message": "Signup successful! User created successfully.",
                "user_info": {
                    "id": str(user.id),
                    "created_at": user.created_at,
                    "username": user.username,
                    "email": user.email,
                    "status": user.status,
                    "role": user.role
                },
                "access_token": access_token,
                "token_type": "bearer"
            }

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Server Error")
