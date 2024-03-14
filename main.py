# import asyncio
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware

# # Define a function to create the FastAPI application
# def create_app():
#     # Import routers inside the function
#     from routers import admin, user, login

#     # Create FastAPI application object
#     app = FastAPI()

#     # Allow CORS for all domains in this example
#     app.add_middleware(
#         CORSMiddleware,
#         allow_origins=["*"],
#         allow_credentials=True,
#         allow_methods=["*"],
#         allow_headers=["*"],
#     )

#     # Include routers
#     app.include_router(login.router, prefix="", tags=["Authentication"])
#     app.include_router(admin.router, prefix="", tags=["Admin"])
#     app.include_router(user.router, prefix="", tags=["User"])

#     return app

# # Call create_app() to obtain the FastAPI application instance
# app = create_app()



# from getpass import getpass  # Use getpass to hide the password input
# from fastapi import FastAPI, Depends, HTTPException, status
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.security import HTTPBasic, HTTPBasicCredentials
# from sqlalchemy.orm import Session
# from admin_database import get_database, verify_hash, Admin
# from typing import Optional, Union
# import os
# import sys

# # Define the function to create the FastAPI application
# def create_app():
#     # Import routers from the 'routers' package using relative imports
#     from routers import admin, user, login

#     # Create FastAPI application object
#     app = FastAPI()

#     # Allow CORS for all domains in this example
#     app.add_middleware(
#         CORSMiddleware,
#         allow_origins=["*"],
#         allow_credentials=True,
#         allow_methods=["*"],
#         allow_headers=["*"],
#     )


#     # Include routers
#     app.include_router(login.router, prefix="", tags=["Authentication"])
#     app.include_router(admin.router, prefix="", tags=["Admin"])
#     app.include_router(user.router, prefix="", tags=["User"])

#     return app


# # Call create_app() to obtain the FastAPI application instance
# app = create_app()


# from authlib.integrations.starlette_client import OAuth
# from starlette.config import Config
# from fastapi import FastAPI, HTTPException
# from starlette.middleware.sessions import SessionMiddleware
# from fastapi.requests import Request
# from pydantic import BaseModel
# from fastapi.security import OAuth2PasswordBearer
# from typing import Any
# from datetime import datetime, timedelta

# app = FastAPI()

# oauth = OAuth()
# SECRET_KEY = "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"
# app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# # Define a generic model for user data
# class UserData(BaseModel):
#     data: Any

# oauth.register(
#     name='google',
#     client_id='274409146209-qp9qp2au3k9bgghu8tb7urf2j7qal8e3.apps.googleusercontent.com',
#     client_secret='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',
#     authorize_url='https://accounts.google.com/o/oauth2/auth',
#     client_kwargs={'scope': 'openid email profile'}
# )

# # Define login route
# @app.get('/login')
# async def login(request: Request):
#     redirect_uri = request.url_for('auth')
#     return await oauth.google.authorize_redirect(request, redirect_uri)

# # Define authentication callback route
# @app.route('/auth')
# async def auth(request: Request):
#     token = await oauth.google.authorize_access_token(request)
#     resp = await oauth.google.get('userinfo', token=token)
#     user_info = resp.json()

#     # Process user information as needed
#     # For now, let's just return it
#     return user_info







# from fastapi import FastAPI, HTTPException, Depends
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from google.oauth2 import id_token
# from google.auth.transport import requests
# from routers import admin, user, login

# app = FastAPI()

# # Allow CORS for all domains in this example
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# class Token(BaseModel):
#     id_token: str

# @app.post("/google-signin")
# async def google_signin(token: Token):
#     try:
#         # Verify the Google ID token
#         ticket = id_token.verify_oauth2_token(token.id_token, requests.Request(), "274409146209-qp9qp2au3k9bgghu8tb7urf2j7qal8e3.apps.googleusercontent.com")
#         print(ticket)
        
#         # Extract user information from the token's payload
#         user_data = {
#             "username": ticket.get("name"),
#             "email": ticket.get("email"),
#             "picture": ticket.get("picture"),
#             "email_verified": ticket.get("email_verified"),
#             "state": ""
#         }

#         return {
#             "message": "Login successful",
#             "userData": user_data
#         }
#     except Exception as e:
#         print(e)
#         raise HTTPException(status_code=500, detail="Server Error")

# # Include routers
# app.include_router(login.router, prefix="", tags=["Authentication"])
# app.include_router(admin.router, prefix="", tags=["Admin"])
# app.include_router(user.router, prefix="", tags=["User"])

# # Main function to run the FastAPI app
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)

# from fastapi import FastAPI, HTTPException, Depends
# from datetime import datetime
# from uuid import uuid4
# from pydantic import BaseModel
# from google.oauth2 import id_token
# from google.auth.transport import requests

# app = FastAPI()

# class Token(BaseModel):
#     id_token: str

# class User(BaseModel):
#     id: str = str(uuid4()) # Generate a random integer ID
#     created_at: datetime = datetime.now()
#     username: str
#     email: str
#     picture: str
#     email_verified: bool
#     role: str = "user"

# @app.post("/google-signin")
# async def google_signin(token: Token):
#     try:
#         # Verify the Google ID token
#         ticket = id_token.verify_oauth2_token(token.id_token, requests.Request(), "274409146209-qp9qp2au3k9bgghu8tb7urf2j7qal8e3.apps.googleusercontent.com")
#         print(ticket)
        
#         # Extract user information from the token's payload
#         user_data = {
#             "username": ticket.get("name"),
#             "email": ticket.get("email"),
#             "picture": ticket.get("picture"),
#             "email_verified": ticket.get("email_verified"),

#         }

#         # Create a User instance with additional fields
#         user = User(**user_data)

#         return {
#             "message": "Login successful",
#             "userData": user.dict()
#         }
#     except Exception as e:
#         print(e)
#         raise HTTPException(status_code=500, detail="Server Error")

# # # Main function to run the FastAPI app
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)


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
app.include_router(admin.router, prefix="", tags=["Admin"])
app.include_router(user.router, prefix="", tags=["User"])

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

@app.post("/google-signin")
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




# Main function to run the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port= 40337)


