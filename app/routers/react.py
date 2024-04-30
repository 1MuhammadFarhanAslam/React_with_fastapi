from fastapi import HTTPException, Depends, APIRouter, Header, Request, status, Form
from datetime import datetime, timedelta, timezone
from google.oauth2 import id_token
from google.auth.transport import requests
import jwt
import os
from models import Google_User, Google_user_Token, Email_User
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy import create_engine
from typing import Generator
from hashing import hash_password
from react_database import verify_email_user_password
from fastapi.responses import JSONResponse
from .Email_Verification import Verification_Token, send_verification_email
import random
import string


router = APIRouter()
# 

# Get the database URL from the environment variable
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL is None:
    raise Exception("DATABASE_URL environment variable is not set")

# Get the database URL from the environment variable
GOOGLE_EMAIL_LOGIN_SECRET_KEY = os.environ.get("GOOGLE_EMAIL_LOGIN_SECRET_KEY")
if GOOGLE_EMAIL_LOGIN_SECRET_KEY is None:
    raise Exception("GOOGLE_EMAIL_LOGIN_SECRET_KEY environment variable is not set")


VERIFICATION_SECRET_KEY = os.environ.get("VERIFICATION_SECRET_KEY")
if VERIFICATION_SECRET_KEY is None:
    raise Exception("VERIFICATION_SECRET_KEY environment variable is not set")

ALGORITHM = "HS256"
PASSWORD_RESET_TOKEN_EXPIRE_MINUTES = 15  # Change to 30 minutes

ACCESS_TOKEN_EXPIRE_MINUTES = 60  # Change to 30 minutes


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

def Email_Verification_Code_Generator():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

def React_JWT_Token(data: dict, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, GOOGLE_EMAIL_LOGIN_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



# @router.post("/api/google-signin", tags=["React"])
# async def google_signin(token: Google_user_Token, db: Session = Depends(get_database)):
#     try:
#         # Verify the Google ID token
#         ticket = id_token.verify_oauth2_token(token.id_token, requests.Request(), "274409146209-qp9qp2au3k9bgghu8tb7urf2j7qal8e3.apps.googleusercontent.com")
        
#         # Extract user information from the token's payload
#         user_data = {
#             "username": ticket.get("name"),
#             "email": ticket.get("email"),
#             "picture": ticket.get("picture"),
#             "email_verified": ticket.get("email_verified"),
#         }

#         # Check if the user already exists in the database
#         existing_user = db.query(Google_User).filter(Google_User.email == user_data["email"]).first()

#         if existing_user:
#             # User exists, return an access token
#             access_token = React_JWT_Token(data={"sub": existing_user.email})
#             print(access_token)

#             return {
#                 "message": "Log-in successfully! User already exists.",
#                 "userData": {
#                     "id": str(existing_user.id),
#                     "username": existing_user.username,
#                     "email": existing_user.email,
#                     "picture": existing_user.picture,
#                     "email_status": existing_user.email_status,
#                     "role": existing_user.role
#                 },

#                 "access_token": access_token,
#                 "token_type": "bearer"
#             }
        
#         else:
#             # User does not exist, create a new user and save it to the database
#             user = Google_User(**user_data)
#             db.add(user)
#             db.commit()
#             db.refresh(user)

#             # Create a new access token for the user
#             access_token = React_JWT_Token(data={"sub": user.email})
#             print(access_token)

#             return {
#                 "message": "Sign-up successfully. User created successfully.",
#                 "userData": {
#                     "id": str(user.id),
#                     "username": user.username,
#                     "email": user.email,
#                     "picture": user.picture,
#                     "email_status": user.email_status,
#                     "role": user.role
#                 },

#                 "access_token": access_token,
#                 "token_type": "bearer"
#             }
    
#     except Exception as e:
#         print(e)
#         raise HTTPException(status_code=500, detail="Server Error")

@router.post("/api/google-signin", tags=["Frontend_Signup/Login"])
async def google_signin(token: Google_user_Token, db: Session = Depends(get_database)):
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

        print("_________user_data__________:", user_data)
        # Check if the user already exists in the database
        existing_user = db.query(Google_User).filter(Google_User.email == user_data["email"]).first()

        if existing_user:
            # User exists, return an access token
            access_token = React_JWT_Token(data={"sub": existing_user.email})
            print(access_token)
            print(type(access_token))

            resp = {
                "message": "Log-in successfully! User already exists.",
                "userData": {
                    "id": existing_user.id,
                    "username": existing_user.username,
                    "email": existing_user.email,
                    "picture": existing_user.picture,
                    "email_status": existing_user.email_status,
                    "roles": existing_user.roles,
                    "status": existing_user.status
                },
                "access_token": access_token,
                "token_type": "bearer"
            }

            print(resp)

            # Set the access token as a cookie
            response = JSONResponse(content=resp)
            response.set_cookie(key="access_token", value=access_token, max_age=1800, secure=False, httponly=True, samesite="none")


            return response
        
        else:
            # User does not exist, create a new user and save it to the database
            user = Google_User(**user_data)
            db.add(user)
            db.commit()
            db.refresh(user)

            # Create a new access token for the user
            access_token = React_JWT_Token(data={"sub": user.email})
            print(access_token)
            print(type(access_token))

            resp = {
                "message": "Sign-up successfully. User created successfully.",
                "userData": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "picture": user.picture,
                    "email_status": user.email_status,
                    "roles": user.roles,
                    "status": user.status
                },
                "access_token": access_token,
                "token_type": "bearer"
            }

            print(resp)

            # Set the access token as a cookie
            response = JSONResponse(content=resp)
            response.set_cookie(key="access_token", value=access_token, max_age=1800, secure=False, httponly=True, samesite="none")

            return response
    
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail= str(e))
    

# @router.post("/api/email-signup", tags=["React"])
# async def email_signup(request: Request, db: Session = Depends(get_database)):
#     try:
#         data = await request.json()
#         email = data.get('email')
#         print("______________email________________: ", email)
#         password = data.get('password')
#         print("______________password________________: ", password)

#         # Check if the user already exists in the database
#         existing_user = db.query(Email_User).filter(Email_User.email == email).first()

#         if existing_user:
#             # User already exists, return his/her details
#             print("______________existing_user________________: ", existing_user)
#             print("messege: User already exists. Please sign in instead.")
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists. Please sign in instead.")  
        
#         else:
#             # User does not exist, proceed with signup.
#             hashed_password = hash_password(password)
#             user = Email_User(email=email, password=hashed_password)
#             db.add(user)
#             db.commit()
#             db.refresh(user)

#             # Create a new access token
#             access_token = React_JWT_Token(data={"sub": user.email})
#             print("_______________access_token_______________", access_token)

#             return {
#                 "message": "Signup successful! User created successfully.",
#                 "user_info": {
#                     "id": user.id,
#                     "created_at": user.created_at,
#                     "email": user.email,
#                     "email_status": user.email_status,
#                     "role": user.role
#                 },

#                 "access_token": access_token,
#                 "token_type": "bearer"
#             }
        
#     except Exception as e:
#         print(e)
#         raise HTTPException(status_code=400, detail="User already exists. Please sign in instead.")

    

# @router.post("/api/email-signin", tags=["React"])
# async def email_signin(request: Request, db: Session = Depends(get_database)):
#     try:
#         data = await request.json()
#         email = data.get('email')
#         print("______________email________________: ", email)
#         password = data.get('password')
#         print("______________password________________: ", password)

#         # Retrieve the user from the database based on the email
#         user = get_email_user(db, email)
#         print("______________user________________: ", user)

#         if not user:
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found. Please sign up first.")
        
#         else:
#             # Verify the password
#             if not verify_email_user_password(password, user.password):
#                 raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect password.")

#             # Generate an access token for the user
#             access_token = React_JWT_Token({"sub": user.email})
#             print("_______________access_token_______________", access_token)

#             return {
#                 "message": "Login successful! User already exists.",
#                 "user_info": {
#                     "id": user.id,
#                     "created_at": user.created_at,
#                     "email": user.email,
#                     "email_status": user.email_status,
#                     "role": user.role
#                 },

#                 "access_token": access_token,
#                 "token_type": "bearer"
#             }

            
#     except Exception as e:
#         raise HTTPException(status_code=400, detail="Error: " + str(e))
    

# @router.post("/api/email-signup", tags=["Frontend_Signup/Login"])
# async def email_signup(request: Request, db: Session = Depends(get_database)):
#     try:
#         data = await request.json()
#         email = data.get('email')
#         print("______________email________________: ", email)
#         print(type(email))
#         password = data.get('password')
#         print("______________password________________: ", password)
#         print(type(password))

#         # Check if the user already exists in the database
#         existing_user = db.query(Email_User).filter(Email_User.email == email).first()

#         if existing_user:
#             # User already exists, return his/her details
#             print("Ooops..................User already exists. Please sign in instead.")
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ooops..................User already exists. Please sign in instead.")  
        
#         else:
#             hashed_password = hash_password(password)
#             user = Email_User(email=email, password=hashed_password)
#             db.add(user)
#             db.commit()
#             db.refresh(user)

#             # Create a new access token
#             access_token = React_JWT_Token(data={"sub": user.email})
#             print("_______________access_token_______________", access_token)
#             print(type(access_token))

#             # Set the access token as a cookie in the response
#             resp = {
#                 "message": "Signup successful! User created successfully.",
#                 "user_info": {
#                     "id": user.id,
#                     "created_at": user.created_at.isoformat(),  # Convert datetime to string,
#                     "email": user.email,
#                     "email_status": user.email_status,
#                     "role": user.role
#                 },

#                 "access_token": access_token,
#                 "token_type": "bearer"
#             }

#             print(resp)

#             # Set the access token as a cookie
#             response = JSONResponse(content=resp)
#             response.set_cookie(key="access_token", value=str(access_token), max_age=1800, secure=False, httponly=True, samesite="none")  # Set cookie for 30 minutes
#             return response
        
#     except Exception as e:
#         print(e)
#         raise HTTPException(status_code=400, detail="Error: " + str(e))

# Email sign up  endpoint with email verification functionality (using SMTP server)
@router.post("/api/email-signup", tags=["Frontend_Signup/Login"])
async def email_signup(request: Request, db: Session = Depends(get_database)):
    try:
        request_data = await request.json()
        print(request_data)
        email = request_data.get('email')
        password = request_data.get('password')
        email_status = request_data.get("email_status")
        roles = request_data.get("roles")
        print("______________roles________________: ", roles)
        status = request_data.get("status")


        # Check if the user already exists in the database
        existing_user = db.query(Email_User).filter(Email_User.email == email).first()

        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists. Please sign in instead.")  
        
        else:
            # # Generate a verification code
            # verification_code = str(uuid4())[:8]  # Generate a random code (e.g., 8 characters)
            # print(f"--------Verification code generated: {verification_code}--------")

            # or
            
            verification_code = Email_Verification_Code_Generator()
            print(f"--------Verification code generated: {verification_code}--------")

            # Generate a verification code
            verification_token = Verification_Token({"email": email})
            print("_______________verification_token_______________", verification_token)
            
            # Send verification email
            hashed_password = hash_password(password)
            user = Email_User(email=email, password=hashed_password, email_status=email_status, roles=roles, status=status, password_reset_code=verification_code, verification_token=verification_token)
            db.add(user)
            db.commit()
            db.refresh(user)

            # send email verification
            send_verification_email(email, verification_token, verification_code)

            # Return success response with access token and user info
            access_token = React_JWT_Token(data={"sub": user.email})
            resp = {
                "message": "Signup successful! Please check your email for verification.",
                "user_info": {
                    "id": user.id,
                    "created_at": user.created_at.isoformat(),
                    "email": user.email,
                    "email_status": user.email_status,
                    "roles": user.roles,
                    "status": user.status
                },
                "access_token": access_token,
                "token_type": "bearer"
            }
            print(resp)

            # Set the access token as a cookie
            response = JSONResponse(content=resp)
            response.set_cookie(key="access_token", value=str(access_token), max_age=1800, secure=False, httponly=True, samesite="none")
            return response
        
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error: " + str(e))
    

@router.post("/api/verification", response_model=None, tags=["Frontend_Signup/Login"])
async def verify_email(request : Request, db: Session = Depends(get_database)):
    try:
        request_data = await request.json()
        print("_______________request_data_______________", request_data)

        verification_code = request_data.get("verification_code")
        print("_______________token_______________", verification_code)

        token = request_data.get("token")
        print("_______________token_______________", token)

        # Decode and verify the verification token
        decoded_token = jwt.decode(token, VERIFICATION_SECRET_KEY, algorithms=["HS256"])
        print("_______________decoded_token_______________", decoded_token)

        email = decoded_token.get("email")
        print("_______________email_______________", email)

        # Find the user by email and mark as verified
        user = db.query(Email_User).filter(Email_User.email == email).first()
        if user:
            # Check if the verification code is correct
            if user.password_reset_code != verification_code:
                raise HTTPException(status_code=400, detail="Verification code is incorrect")
            if user.verification_token != token:
                raise HTTPException(status_code=400, detail="Verification token is Invalid")
            
            # Check if the access token is valid (not expired)
            exp_timestamp = decoded_token["exp"]
            exp_datetime_utc = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
            if datetime.now(timezone.utc) >= exp_datetime_utc:
                raise HTTPException(status_code=400, detail="Password reset token has expired. Send Forgot Password request again.")
            
            # Return success response with access token and user info
            access_token = React_JWT_Token(data={"sub": user.email})

            user.email_status = "Verified"
            user.password_reset_code = None
            user.password_reset_code = None
            db.commit()
            db.refresh(user)
            
            print("-----------Email verified successfully-----------")

            resp = {"message": "Email verified successfully",
                    "user_info": {
                        "id": user.id,
                        "created_at": user.created_at.isoformat(),
                        "email": user.email,
                        "email_status": user.email_status,
                        "roles": user.roles,
                        "status": user.status
                    },
                "access_token": access_token,
                "token_type": "bearer"
            }

            # Set the access token as a cookie
            response = JSONResponse(content=resp)
            response.set_cookie(key="access_token", value=str(access_token), max_age=1800, secure=False, httponly=True, samesite="none")
            return response
        else:
            raise HTTPException(status_code=400, detail="User does not exist")
        
    except jwt.exceptions.DecodeError:
        raise HTTPException(status_code=400, detail="Invalid token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Token has expired")
    except Exception as e:
        raise HTTPException(status_code=400, detail= str(e))

        

# Your existing endpoint code for email signin
@router.post("/api/email-signin", tags=["Frontend_Signup/Login"])
async def email_signin(request: Request, db: Session = Depends(get_database)):
    try:
        data = await request.json()
        email = data.get('email')
        print("______________email________________: ", email)
        print(type(email))
        password = data.get('password')
        print("______________password________________: ", password)
        print(type(password))

        # Check if the email exists in the database
        email_user = db.query(Email_User).filter(Email_User.email == email).first()

        if not email_user:
            print("OooPS...User not found. Please sign up first.")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OooPS...User not found. Please sign up first.")
        
        else:
            # Verify the password
            if not verify_email_user_password(password, email_user.password):
                print("OooPS...Incorrect password. Please try again")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OooPS...Incorrect password. Please try again")
            
            # elif email_user.email_status == "unverified":
            #     print("OooPS...You have not verified yet. Please verify your email first...")
            #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You have not verified yet.Please verify your email first.")
            
            else:
                # Generate an access token for the user
                access_token = React_JWT_Token({"sub": email_user.email})
                print("_______________access_token_______________", access_token)
                print(type(access_token))

                # Set the access token as a cookie in the response
                resp = {
                    "message": "Login successful! User already exists.",
                    "user_info": {
                        "id": email_user.id,
                        "created_at": email_user.created_at.isoformat(),  # Convert datetime to string,
                        "email": email_user.email,
                        "email_status": email_user.email_status,
                        "roles": email_user.roles,
                        "status": email_user.status
                    },

                    "access_token": access_token,
                    "token_type": "bearer"
                }

                print(resp)

                # Set the access token as a cookie
                response = JSONResponse(content=resp)
                response.set_cookie(key="access_token", value=str(access_token),max_age=1800, secure=False, httponly=True, samesite="none")  # Set cookie for 30 minutes
                return response
            
    except Exception as e:
        raise HTTPException(status_code=400, detail= str(e))
    


@router.get("/api/auth/user", response_model=None, tags=["Frontend_Signup/Login"])
async def combined_user_auth(
    authorization: str = Header(...),  # Get the access token from the Authorization header
    db: Session = Depends(get_database)
):
    try:
        # Extract the token from the Authorization header
        token = authorization.split(" ")[1]  # Assuming the header format is "Bearer <token>"
        
        # Decode and verify the JWT token
        decoded_token = jwt.decode(token, GOOGLE_EMAIL_LOGIN_SECRET_KEY, algorithms=[ALGORITHM])
        print("________________decoded_token________________", decoded_token)
        email = decoded_token.get("sub")  # Assuming "sub" contains the email address
        
        # Query the database based on the email to get user data from Google_User and Email_User
        google_user = db.query(Google_User).filter(Google_User.email == email).first()
        email_user = db.query(Email_User).filter(Email_User.email == email).first()
        print("_______________user details in jwt token (Google_User)___________" , google_user)
        print("_______________user details in jwt token (Email_User)___________" , email_user)
        
        if google_user:
            user_data = {
                "id": str(google_user.id),
                "created_at": google_user.created_at,
                "username": google_user.username,
                "email": google_user.email,
                "picture": google_user.picture,
                "email_status": google_user.email_status,
                "roles": google_user.roles,
                "status": google_user.status
            }

            print("_______________user details_______________", user_data)

        elif email_user:
            user_data = {
                "id": email_user.id,
                "created_at": email_user.created_at,
                "email": email_user.email,
                "email_status": email_user.email_status,
                "roles": email_user.roles,
                "status": email_user.status,
            }

            print("_______________user details_______________", user_data)

        else:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "message": "User details retrieved successfully",
            "userData": user_data
        }
    except jwt.exceptions.DecodeError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except Exception as e:
        raise HTTPException(status_code=400, detail= str(e))
    


    
