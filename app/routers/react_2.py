from fastapi import HTTPException, APIRouter, Request, Header, Depends, Form
import requests
from fastapi.responses import FileResponse
import tempfile
import os
import jwt
from sqlalchemy.orm import Session
from models import React_User, Email_User, AccessToken
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine
from typing import Generator
from jwt.exceptions import ExpiredSignatureError  # Import the ExpiredSignatureError
from fastapi import UploadFile, File
from typing import Optional
import logging
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from datetime import datetime


router = APIRouter()

# 

# Get the database URL from the environment variable
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL is None:
    raise Exception("DATABASE_URL environment variable is not set")

GOOGLE_EMAIL_LOGIN_SECRET_KEY = os.environ.get("GOOGLE_EMAIL_LOGIN_SECRET_KEY")
if GOOGLE_EMAIL_LOGIN_SECRET_KEY is None:
    raise Exception("GOOGLE_EMAIL_LOGIN_SECRET_KEY environment variable is not set")

access_token = os.environ.get("ACCESS_TOKEN")
if access_token is None:
    raise Exception("ACCESS_TOKEN environment variable is not set")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Change to 30 minutes

nginx_url = "http://85.239.241.96"
    

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


# def create_session():
#     session = requests.Session()
#     retries = Retry(total=1, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
#     adapter = HTTPAdapter(max_retries=retries)
#     session.mount('http://', adapter)
#     session.mount('https://', adapter)
#     return session


# @router.post("/api/ttm_endpoint")
# async def text_to_music(request: Request):
#     try:
#         # Extract the request data
#         request_data = await request.json()
#         print('_______________request_data_____________', request_data)
#         prompt = request_data.get("prompt")
#         print('_______________prompt_____________', prompt)
#         if prompt is None:
#             print('_______________prompt_____________', prompt)
#             raise HTTPException(status_code=400, detail="Prompt is missing in the request body.")
        
        
#         try:
#             # Log in the user and get the access token and corresponding URL
#             data = {"prompt": prompt}
            

#             # Construct the TTS URL based on successful login URL
#             headers = {
#                 "Accept": "audio/wav",
#                 "Authorization": f"Bearer {access_token}",
#                 "Content-Type": "application/json"
#             }

#             print('________________data________________', data)
#             print('______________access_token______________', access_token)
#             print('________header_________', headers)

#             response = requests.post(f"{nginx_url}/api/ttm_endpoint", headers=headers, json=data)
#             print('______________response_____________')

#             if response.status_code == 200:
#                 # Create a temporary file to save the audio data
#                 with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
#                     temp_file.write(response.content)
#                     temp_file_path = temp_file.name

#                 # Return the temporary file using FileResponse
#                 return FileResponse(temp_file_path, media_type="audio/wav", filename="generated_ttm_audio.wav")
#             else:
#                 print('________________response.text________________')
#                 raise HTTPException(status_code=response.status_code, detail=response.text)

#         except ExpiredSignatureError:
#             raise HTTPException(status_code=401, detail="JWT token has expired. Please log in again.")

#     except ValueError:
#         raise HTTPException(status_code=400, detail="Invalid JSON format in the request headers")



@router.post("/api/ttm_endpoint")
async def text_to_music(request: Request):
    try:
        # Extract the request data
        request_data = await request.json()
        prompt = request_data.get("prompt")
        if prompt is None:
            raise HTTPException(status_code=400, detail="Prompt is missing in the request body.")
        

        # Log in the user and get the access token and corresponding URL
        # Assuming access_token is obtained somehow
        access_token = "ACCESS_TOKEN"
        
        data = {
            "prompt": prompt
        }

        headers = {
            "Accept": "audio/wav",
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        response = requests.post(f"{nginx_url}/api/ttm_endpoint", headers=headers, json=data)

        if response.status_code == 200:
            # Create a temporary file to save the audio data
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(response.content)
                temp_file_path = temp_file.name

            # Return the temporary file using FileResponse
            return FileResponse(temp_file_path, media_type="audio/wav", filename="generated_ttm_audio.wav")
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)

    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="JWT token has expired. Please log in again.")

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid JSON format in the request headers")
