from fastapi import HTTPException, APIRouter, Request, Header, Depends, Form
import requests
from fastapi.responses import FileResponse, JSONResponse
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
from datetime import datetime, timedelta
import time
import asyncio
import httpx
from requests.exceptions import Timeout
from httpx import Timeout as HTTPXTimeout
import aiohttp
from aiohttp import web
import json






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


# def create_session():   #session is usually used to make a request redirect to another server
#     session = requests.Session()
#     retries = Retry(total=1, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
#     adapter = HTTPAdapter(max_retries=retries)
#     session.mount('http://', adapter)
#     session.mount('https://', adapter)
#     return session

#----------Working ndpoint------------------------TTM endpoint with auth_token from header,duration and timeout with requests library--------------
# ----------------This endpoint sends requests (using requests library (may be in series manner but not sure)) to the TTM endpoint and returns the response to the client.
# @router.post("/api/ttm_endpoint")
# async def text_to_music(request: Request, authorization: str = Header(...), db: Session = Depends(get_database)):
#     try:
#         # Extract the request data
#         request_data = await request.json()
#         print('_______________request_data_____________', request_data)

#         prompt = request_data.get("prompt")
#         print('_______________prompt_____________', prompt)
#         duration = request_data.get("duration")
#         print('_______________duration_____________', duration)
#         authorization = request_data.get("authorization")
#         print('_______________authorization_____________', authorization)

#         if prompt is None:
#             raise HTTPException(status_code=400, detail="Prompt is missing in the request body.")

#         # Check if the Authorization header is present
#         if authorization is None:
#             raise HTTPException(status_code=401, detail="Authorization header is missing.")
        
#         # Extract the token from the Authorization header
#         token = authorization.split(" ")[1]  # Assuming the header format is "Bearer <token>"
        
#         try:
#             # Decode and verify the JWT token (if needed)
#             decoded_token = jwt.decode(token, GOOGLE_EMAIL_LOGIN_SECRET_KEY, algorithms=[ALGORITHM])
#             email = decoded_token.get("sub")

#             # Query the database based on the email to get user data from React_User and Email_User
#             react_user = db.query(React_User).filter(React_User.email == email).first()
#             email_user = db.query(Email_User).filter(Email_User.email == email).first()

#             # If the user is not registered in either React_User or Email_User, raise an exception
#             if not react_user and not email_user:
#                 raise HTTPException(status_code=401, detail="User is not registered.")
        
        
#             # Log in the user and get the access token and corresponding URL
#             data = {"prompt": prompt, "duration": duration}
            
#             # Construct the TTM URL based on successful login URL
#             headers = {
#                 "Accept": "audio/wav",
#                 "Authorization": f"Bearer {access_token}",
#                 "Content-Type": "application/json"
#             }

#             print('________________data________________', data)
#             print('______________access_token______________', access_token)
#             print('________header_________', headers)

#             # Set the timeout value in seconds (e.g., 30 seconds)
#             timeout = 30
#             try:
#                 # Make a POST request to the TTM endpoint
#                 response = requests.post(f"{nginx_url}/api/ttm_endpoint", headers=headers, json=data, timeout=timeout)
#                 print('______________response_____________:', response)


#                 if response.status_code == 200:
#                     # Create a temporary file to save the audio data
#                     with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
#                         temp_file.write(response.content)
#                         temp_file_path = temp_file.name

#                     # Return the temporary file using FileResponse
#                     return FileResponse(temp_file_path, media_type="audio/wav", filename="generated_ttm_audio.wav")
#                 else:
#                     print('________________response.text________________')
#                     raise HTTPException(status_code=response.status_code, detail=response.text)
                
#             except Timeout:
#                 raise HTTPException(status_code=504, detail="Gateway Timeout: The server timed out waiting for the request.")

#         except ExpiredSignatureError:
#             raise HTTPException(status_code=401, detail="JWT token has expired. Please log in again.")
            

#     except ValueError:
#         raise HTTPException(status_code=400, detail="Invalid JSON format in the request headers")

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------


#-------------Working endpoint---------------------- TTM endpoint without auth_token from header, using requests library and time out functionality------------
# ----------------This endpoint sends requests (using requests library in series manner) to the TTM endpoint and returns the response to the client.
# @router.post("/api/ttm_endpoint")
# async def text_to_music(request: Request):
#     try:
#         request_data = await request.json()
#         print('_______________request_data_____________', request_data)

#         prompt = request_data.get("prompt")
#         print('_______________prompt_____________', prompt)

#         duration = request_data.get("duration")
#         print('_______________duration_____________', duration)

#         if prompt is None:
#             raise HTTPException(status_code=400, detail="Prompt is missing in the request body.")


#         data = {"prompt": prompt, "duration": duration}
#         headers = {
#             "Accept": "audio/wav",
#             "Authorization": f"Bearer {access_token}",
#             "Content-Type": "application/json"
#         }

#         # Set the timeout value in seconds (e.g., 30 seconds)
#         timeout = 60

#         try:
#             response = requests.post(
#                 f"{nginx_url}/api/ttm_endpoint",
#                 headers=headers,
#                 json=data,
#                 timeout=timeout  # Add the timeout parameter here
#             )
#         except Timeout:
#             raise HTTPException(status_code=504, detail="-------------Gateway Timeout: The server timed out waiting for the request----------")

#         if response.status_code == 200:
#             with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
#                 temp_file.write(response.content)
#                 temp_file_path = temp_file.name

#             return FileResponse(temp_file_path, media_type="audio/wav", filename="generated_ttm_audio.wav")
#         else:
#             raise HTTPException(status_code=response.status_code, detail=response.text)

#     except ValueError:
#         raise HTTPException(status_code=400, detail="Invalid JSON format in the request headers")



#---------------Working endpoint-------------------- TTM endpoint without auth_token from header, using requests library and time out functionality------------
# ----------------This endpoint sends requests (using aiohttp library in parallel manner) --------------------- 
#-----------This endpoint is not same as above instead it has different use case of try block---------------------
# @router.post("/api/ttm_endpoint")
# async def ttm_endpoint(request : Request):
#     try:
#         # Extract the request data
#         request_data = await request.json()
#         print('_______________request_data_____________', request_data)
#         prompt = request_data.get("prompt")
#         print('_______________prompt_____________', prompt)
#         duration = request_data.get("duration")
#         print('_______________duration_____________', duration)

#         if prompt is None:
#             raise HTTPException(status_code=400, detail="Prompt is missing in the request body.")
        
#         try:
#             # Construct the TTS URL based on successful login URL
#             data = {"prompt": prompt, "duration": duration}
            
#             # Construct headers (modify as needed)
#             headers = {
#                 "Accept": "audio/wav",
#                 "Authorization": f"Bearer {access_token}",  # Replace access_token with your token
#                 "Content-Type": "application/json"
#             }

#             print('________________data________________', data)
#             print('________header_________', headers)

#             async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
#                 async with session.post(f"{nginx_url}/api/ttm_endpoint", headers=headers, json=data) as response:
#                     print('________response_________', response)
#                     response_data = await response.read()
                    
#             if response.status == 200:
#                 # Process the response and return the audio file
#                 temp_file_path = "/path/to/temp_file.wav"  # Replace with actual file path
#                 with open(temp_file_path, "wb") as temp_file:
#                     temp_file.write(response_data)

#                 return FileResponse(temp_file_path, headers={"Content-Type": "audio/wav"})
#             else:
#                 raise HTTPException(status_code=response.status, detail=response.text)

#         except asyncio.TimeoutError:
#             raise HTTPException(status_code=504, detail="--------Gateway Timeout: The server timed out waiting for the request----------------")

#     except json.JSONDecodeError:
#         raise HTTPException(status_code=400, detail="Invalid JSON format in the request headers")




#--------------Working endpoint--------------------- TTM endpoint without auth_token from header, using httpx library and time out functionality------------
# ----------------This endpoint sends requests (using httpx library in parallel manner) to the TTM endpoint and returns the response to the client.
@router.post("/api/ttm_endpoint")
async def text_to_music(request: Request):
    try:
        # Extract the request data
        request_data = await request.json()
        print('_______________request_data_____________', request_data)

        prompt = request_data.get("prompt")
        print('_______________prompt_____________', prompt)

        duration = request_data.get("duration")
        print('_______________duration_____________', duration)

        if prompt is None:
            print('_______________prompt_____________', prompt)
            raise HTTPException(status_code=400, detail="Prompt is missing in the request body.")
        
        
        try:
            # Log in the user and get the access token and corresponding URL
            data = {"prompt": prompt, "duration": duration}
            

            # Construct the TTM URL based on successful login URL
            headers = {
                "Accept": "audio/wav",
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }

            print('________________data________________', data)
            print('______________access_token______________', access_token)
            print('________header_________', headers)

            # Set a longer timeout value in seconds (e.g., 60 seconds)
            # timeout = HTTPXTimeout(timeout=6000)

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{nginx_url}/api/ttm_endpoint",
                    headers=headers,
                    json=data,
                )

            if response.status_code == 200:
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                    temp_file.write(response.content)
                    temp_file_path = temp_file.name

                return FileResponse(temp_file_path, media_type="audio/wav", filename="generated_ttm_audio.wav")
            else:
                raise HTTPException(status_code=response.status_code, detail=response.text)
            
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="-------------Gateway Timeout: The server timed out waiting for the request----------")

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid JSON format in the request headers")




#---------------Working endpoint-------------------- TTM endpoint without auth_token from header, using requests library and time out functionality------------
# ----------------This endpoint sends requests (using requests library in parallel manner) --------------------- 
#-----------This endpoint is not same as above instead it has different use case of try block---------------------
# @router.post("/api/ttm_endpoint")
# async def text_to_music(request: Request):
#     try:
#         # Extract the request data
#         request_data = await request.json()
#         print('_______________request_data_____________', request_data)
#         prompt = request_data.get("prompt")
#         print('_______________prompt_____________', prompt)
#         duration = request_data.get("duration")
#         print('_______________duration_____________', duration)

#         if prompt is None:
#             raise HTTPException(status_code=400, detail="Prompt is missing in the request body.")
        
#         try:
#             # Log in the user and get the access token and corresponding URL
#             data = {"prompt": prompt, "duration": duration}
            

#             # Construct the TTS URL based on successful login URL
#             headers = {
#                 "Accept": "audio/wav",
#                 "Authorization": f"Bearer {access_token}",
#                 "Content-Type": "application/json"
#             }

#             print('________________data________________', data)
#             print('______________access_token______________', access_token)
#             print('________header_________', headers)

#             async with httpx.AsyncClient() as client:
#                 response = await client.post(f"{nginx_url}/api/ttm_endpoint", headers=headers, json=data)
#                 print('________response_________', response)

#             if response.status_code == 200:
#                 with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
#                     temp_file.write(response.content)
#                     temp_file_path = temp_file.name

#                 return FileResponse(temp_file_path, media_type="audio/wav", filename="generated_ttm_audio.wav")
#             else:
#                 raise HTTPException(status_code=response.status_code, detail=response.text)
            
#         except httpx.ReadTimeout:
#             raise HTTPException(status_code=504, detail="-------------Gateway Timeout: The server timed out waiting for the request----------")

#     except ValueError:

#         raise HTTPException(status_code=400, detail="Invalid JSON format in the request headers")
    

