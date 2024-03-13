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




# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from fastapi.security import OAuth2PasswordBearer
# from typing import Any
# from datetime import datetime, timedelta
# import jwt
# from fastapi.middleware.cors import CORSMiddleware

# app = FastAPI()

# app.add_middleware(
#         CORSMiddleware,
#         allow_origins=["*"],
#         allow_credentials=True,
#         allow_methods=["*"],
#         allow_headers=["*"],
#     )

# # Define a generic model for user data
# class UserData(BaseModel):
#     data: Any

# # Route for Google sign-in
# @app.post("/google-signin")
# async def google_signin(user_data: UserData):
#     try:
#         # Extract user information from the payload
#         data = user_data.data
        
#         # Here you can process the user data as needed, once you know its format
#         # For now, let's just print it
#         print(f"Received user data: {data}")

#         # # For demonstration, let's create a dummy user
#         # user_id = 1

#         # # Create a JWT token
#         # token_expiry = datetime.utcnow() + timedelta(hours=24)
#         # token = jwt.encode({"userId": user_id, "exp": token_expiry}, "secret-key", algorithm="HS256")

#         # # Your Redis storage logic here
#         # # For demonstration, let's just print the token
#         # print(f"Token: {token}")

#         # return {
#         #     "message": "Login successful",
#         #     "token": token.decode('utf-8')
#         # }
#     except Exception as e:
#         print(f"Error: {e}")
#         raise HTTPException(status_code=500, detail="Server Error")

# # Main function to run the FastAPI app
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)


from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import requests

router = APIRouter()

# Assuming you have already configured googleClient and redis
# Replace process.env.googleClientId with your actual Google Client ID

class GoogleSignInData(BaseModel):
    id_token: str

@router.post("/google-signin", response_model=dict)
async def google_signin(data: GoogleSignInData):
    try:
        # Validate Google ID token
        response = requests.post('https://oauth2.googleapis.com/tokeninfo', data={'id_token': data.id_token})
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Invalid Google ID token")

        payload = response.json()

        # Check if the user exists in the database
        # You'll need to replace this with your database query logic
        # For demonstration purposes, I'm just using a placeholder user object
        user = {"name": payload.get("name"), "email": payload.get("email"), "state": ""}

        # Here you can perform actions like database queries to check if the user exists, and create/update the user if necessary
        # For this example, I'm assuming you have already implemented this logic

        # Create a JWT token
        token = jwt.encode({"userId": user["id"]}, "secret-key", algorithm="HS256")

        return JSONResponse(content={"message": "Login successful", "token": token})

    except Exception as e:
        # Log the error
        print("Error:", e)
        # Return error response
        return JSONResponse(status_code=500, content={"message": "Server Error"})