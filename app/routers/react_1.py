# from fastapi import HTTPException, APIRouter, Request
# import requests
# from fastapi.responses import FileResponse
# import tempfile

# router = APIRouter()

# # @router.post("/api/ttm_endpoint")
# # async def text_to_music(request: Request):
# #     try:
# #         request_data = await request.json()
# #         prompt = request_data.get("prompt")
# #         if prompt is None:
# #             raise HTTPException(status_code=400, detail="Prompt is missing in the request body")

# #         authorization = request.headers.get("Authorization")
# #         if authorization is None:
# #             raise HTTPException(status_code=401, detail="Authorization header is missing")
        
# #         parts = authorization.split()
# #         if len(parts) != 2 or parts[0].lower() != "bearer":
# #             raise HTTPException(status_code=401, detail="Invalid Authorization header format")
        
# #         access_token = parts[1]

# #         data = {
# #             "prompt": prompt
# #         }

# #         ttm_url = "http://149.11.242.18:14094/ttm_service"  # Adjust the URL as needed
# #         headers = {
# #             "Accept": "audio/wav",  # Specify the desired audio format
# #             "Authorization": f"Bearer {access_token}",
# #             "Content-Type": "application/json"
# #         }
# #         response = requests.post(ttm_url, headers=headers, json=data)

# #         if response.status_code == 200:
# #             # Create a temporary file to save the audio data
# #             with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
# #                 temp_file.write(response.content)
# #                 temp_file_path = temp_file.name

# #             # Return the temporary file using FileResponse
# #             return FileResponse(temp_file_path, media_type="audio/wav", filename="generated_audio.wav")
# #         else:
# #             raise HTTPException(status_code=response.status_code, detail=response.text)

# #     except ValueError:
# #         raise HTTPException(status_code=400, detail="Invalid JSON format in the request body")


# # Define constants for login credentials
# LOGIN_USERNAME = "Opentensor@hotmail.com"
# LOGIN_PASSWORD = "Opentensor@12345"

# # Define a function to check if the user is logged in
# def is_user_logged_in():
#     # Make a request to the login endpoint to check if the user is logged in
#     login_url = "http://149.11.242.18:14094/login"  # Adjust the URL as needed
#     login_payload = {
#         "username": LOGIN_USERNAME,
#         "password": LOGIN_PASSWORD
#     }
#     login_headers = {
#         "accept": "application/json",
#         "Content-Type": "application/x-www-form-urlencoded"
#     }
#     login_response = requests.post(login_url, headers=login_headers, data=login_payload)

#     if login_response.status_code == 200:
#         # User is logged in, return True
#         return True
#     else:
#         # User is not logged in, return False
#         return False

# # Define a function to log in the user
# def login_user():
#     # Make a request to the login endpoint to log in the user
#     login_url = "http://149.11.242.18:14094/login"  # Adjust the URL as needed
#     login_payload = {
#         "username": LOGIN_USERNAME,
#         "password": LOGIN_PASSWORD
#     }
#     login_headers = {
#         "accept": "application/json",
#         "Content-Type": "application/x-www-form-urlencoded"
#     }
#     login_response = requests.post(login_url, headers=login_headers, data=login_payload)

#     if login_response.status_code == 200:
#         # Login successful
#         return True
#     else:
#         # Login failed
#         return False

# @router.post("/api/ttm_endpoint")
# async def text_to_music(request: Request):
#     try:
#         request_data = await request.json()
#         prompt = request_data.get("prompt")
#         if prompt is None:
#             raise HTTPException(status_code=400, detail="Prompt is missing in the request body")

#         # Check if the user is logged in
#         if not is_user_logged_in():
#             # User is not logged in, try to log in
#             login_success = login_user()
#             if not login_success:
#                 raise HTTPException(status_code=401, detail="Login failed. User is not logged in.")

#         # Proceed with generating audio data
#         access_token = "your_access_token_here"  # Placeholder for the actual access token

#         data = {
#             "prompt": prompt
#         }

#         ttm_url = "http://149.11.242.18:14094/ttm_service"  # Adjust the URL as needed
#         headers = {
#             "Accept": "audio/wav",  # Specify the desired audio format
#             "Authorization": f"Bearer {access_token}",
#             "Content-Type": "application/json"
#         }
#         response = requests.post(ttm_url, headers=headers, json=data)

#         if response.status_code == 200:
#             # Create a temporary file to save the audio data
#             with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
#                 temp_file.write(response.content)
#                 temp_file_path = temp_file.name

#             # Return the temporary file using FileResponse
#             return FileResponse(temp_file_path, media_type="audio/wav", filename="generated_audio.wav")
#         else:
#             raise HTTPException(status_code=response.status_code, detail=response.text)

#     except ValueError:
#         raise HTTPException(status_code=400, detail="Invalid JSON format in the request body")



from fastapi import HTTPException, APIRouter, Request, Header, Depends
import requests
from fastapi.responses import FileResponse
import tempfile
import os
import jwt
from sqlalchemy.orm import Session
from models import React_User, Email_User
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine
from typing import Generator
from jwt.exceptions import ExpiredSignatureError  # Import the ExpiredSignatureError
from fastapi import UploadFile, File
from typing import Annotated


router = APIRouter()

# 

# Get the database URL from the environment variable
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL is None:
    raise Exception("DATABASE_URL environment variable is not set")

GOOGLE_EMAIL_LOGIN_SECRET_KEY = os.environ.get("GOOGLE_EMAIL_LOGIN_SECRET_KEY")
if GOOGLE_EMAIL_LOGIN_SECRET_KEY is None:
    raise Exception("GOOGLE_EMAIL_LOGIN_SECRET_KEY environment variable is not set")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

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


# Define constants for login credentials
LOGIN_USERNAME = "Opentensor@hotmail.com"
LOGIN_PASSWORD = "Opentensor@123"

# Define a function to log in the user and get the access token
def login_user():
    # Make a request to the login endpoint to log in the user
    login_url = "http://38.80.122.248:40337/login"  # Adjust the URL as needed
    login_payload = {
        "username": LOGIN_USERNAME,
        "password": LOGIN_PASSWORD
    }
    login_headers = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    login_response = requests.post(login_url, headers=login_headers, data=login_payload)

    if login_response.status_code == 200:
        # Login successful, extract and return the access token
        response_data = login_response.json()
        access_token = response_data.get("access_token")
        return access_token
    else:
        # Login failed
        return None

# @router.post("/api/ttm_endpoint")
# async def text_to_music(request: Request):
#     try:
#         request_data = await request.json()
#         prompt = request_data.get("prompt")
#         if prompt is None:
#             raise HTTPException(status_code=400, detail="Prompt is missing in the request body")
        
#         # Log in the user and get the access token
#         access_token = login_user()

#         # Proceed with generating audio data using the obtained access token
#         data = {
#             "prompt": prompt
#         }

#         ttm_url = "http://38.80.122.248:40337/ttm_service"  # Adjust the URL as needed
#         headers = {
#             "Accept": "audio/wav",  # Specify the desired audio format
#             "Authorization": f"Bearer {access_token}",
#             "Content-Type": "application/json"
#         }
#         response = requests.post(ttm_url, headers=headers, json=data)

#         if response.status_code == 200:
#             # Create a temporary file to save the audio data
#             with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
#                 temp_file.write(response.content)
#                 temp_file_path = temp_file.name

#             # Return the temporary file using FileResponse
#             return FileResponse(temp_file_path, media_type="audio/wav", filename="generated_audio.wav")
#         else:
#             raise HTTPException(status_code=response.status_code, detail=response.text)

#     except ValueError:
#         raise HTTPException(status_code=400, detail="Invalid JSON format in the request body")


@router.post("/api/tts_endpoint")
async def text_to_speech(request: Request, authorization: str = Header(None), db: Session = Depends(get_database))  -> FileResponse:
    try:
        # Extract the request data
        request_data = await request.json()
        print("________________request_data________________", request_data)
        prompt = request_data.get("prompt")
        print("________________prompt________________", prompt)
        
        if prompt is None:
            print("Prompt is missing in the request body.")
            raise HTTPException(status_code=400, detail="Prompt is missing in the request body.")

        # Check if the Authorization header is present
        if authorization is None:
            print("Authorization header is missing.")
            raise HTTPException(status_code=401, detail="Authorization header is missing.")
        
        # Extract the token from the Authorization header
        token = authorization.split(" ")[1]  # Assuming the header format is "Bearer <token>"
        
        try:
            # Decode and verify the JWT token
            decoded_token = jwt.decode(token, GOOGLE_EMAIL_LOGIN_SECRET_KEY, algorithms=[ALGORITHM])
            print("________________decoded_token________________", decoded_token)

            email = decoded_token.get("sub")  # Assuming "sub" contains the email address
            print("________________email________________", email)
            
            # Query the database based on the email to get user data from React_User and Email_User
            react_user = db.query(React_User).filter(React_User.email == email).first()
            email_user = db.query(Email_User).filter(Email_User.email == email).first()
            print("_______________user details in jwt token (React_User)___________" , react_user)
            print("_______________user details in jwt token (Email_User)___________" , email_user)

            # If the user is not registered in either React_User or Email_User, raise an exception
            if not react_user and not email_user:
                raise HTTPException(status_code=401, detail="___________User is not registered___________")
            
            else:
                # Log in the user and get the access token
                access_token = login_user()
                print("_______________access_token___________" , access_token)

                data = {
                    "prompt": prompt
                }

                ttm_url = "http://38.80.122.248:40337/tts_service"  # Adjust the URL as needed
                headers = {
                    "Accept": "audio/wav",  # Specify the desired audio format
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }

                response = requests.post(ttm_url, headers=headers, json=data)

                if response.status_code == 200:
                    # Create a temporary file to save the audio data
                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                        temp_file.write(response.content)
                        temp_file_path = temp_file.name

                    # Return the temporary file using FileResponse
                    return FileResponse(temp_file_path, media_type="audio/wav", filename="generated_tts_audio.wav")
                else:
                    raise HTTPException(status_code=response.status_code, detail=response.text)

        except ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="JWT token has expired. Please log in again.")

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid JSON format in the request headers")



@router.post("/api/ttm_endpoint")
async def text_to_music(request: Request, authorization: str = Header(None), db: Session = Depends(get_database))  -> FileResponse:
    try:
        # Extract the request data
        request_data = await request.json()
        print("________________request_data________________", request_data)
        prompt = request_data.get("prompt")
        print("________________prompt________________", prompt)
        
        if prompt is None:
            print("Prompt is missing in the request body.")
            raise HTTPException(status_code=400, detail="Prompt is missing in the request body.")

        # Check if the Authorization header is present
        if authorization is None:
            print("Authorization header is missing.")
            raise HTTPException(status_code=401, detail="Authorization header is missing.")
        
        # Extract the token from the Authorization header
        token = authorization.split(" ")[1]  # Assuming the header format is "Bearer <token>"
        
        try:
            # Decode and verify the JWT token
            decoded_token = jwt.decode(token, GOOGLE_EMAIL_LOGIN_SECRET_KEY, algorithms=[ALGORITHM])
            print("________________decoded_token________________", decoded_token)

            email = decoded_token.get("sub")  # Assuming "sub" contains the email address
            print("________________email________________", email)
            
            # Query the database based on the email to get user data from React_User and Email_User
            react_user = db.query(React_User).filter(React_User.email == email).first()
            email_user = db.query(Email_User).filter(Email_User.email == email).first()
            print("_______________user details in jwt token (React_User)___________" , react_user)
            print("_______________user details in jwt token (Email_User)___________" , email_user)

            # If the user is not registered in either React_User or Email_User, raise an exception
            if not react_user and not email_user:
                raise HTTPException(status_code=401, detail="___________User is not registered___________")
            
            else:
                # Log in the user and get the access token
                access_token = login_user()
                print("_______________access_token___________" , access_token)

                data = {
                    "prompt": prompt
                }

                ttm_url = "http://38.80.122.248:40337/ttm_service"  # Adjust the URL as needed
                headers = {
                    "Accept": "audio/wav",  # Specify the desired audio format
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }

                response = requests.post(ttm_url, headers=headers, json=data)

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
    

    

@router.post("/api/vc_endpoint")
async def voice_clone(
    request: Request,
    audio_file: UploadFile = File(...),
    authorization: str = Header(None),
    db: Session = Depends(get_database)
) -> FileResponse:
    try:
        # Extract the request data
        request_data = await request.json()
        print("________________request_data________________", request_data)
        prompt = request_data.get("prompt")
        print("________________prompt________________", prompt)

        # Validate prompt
        if not prompt:
            raise HTTPException(status_code=400, detail="Prompt is missing in the request body.")

        # Check if the Authorization header is present
        if authorization is None:
            raise HTTPException(status_code=401, detail="Authorization header is missing.")

        # Extract the token from the Authorization header
        token = authorization.split(" ")[1]  # Assuming the header format is "Bearer <token>"

        try:
            # Decode and verify the JWT token
            decoded_token = jwt.decode(token, GOOGLE_EMAIL_LOGIN_SECRET_KEY, algorithms=[ALGORITHM])
            email = decoded_token.get("sub")  # Assuming "sub" contains the email address

            # Query the database based on the email to get user data from React_User and Email_User
            react_user = db.query(React_User).filter(React_User.email == email).first()
            email_user = db.query(Email_User).filter(Email_User.email == email).first()

            # If the user is not registered in either React_User or Email_User, raise an exception
            if not react_user and not email_user:
                raise HTTPException(status_code=401, detail="User is not registered.")

            else:
                # Log in the user and get the access token
                access_token = login_user()

                data = {
                    "prompt": prompt
                }

                # Adjust the URL to point to API no 1 (/vc_service)
                vc_service_url = "http://38.80.122.248:40337/vc_service"  # Adjust the URL as needed
                headers = {
                    "Accept": "audio/wav",  # Specify the desired audio format
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "multipart/form-data"
                }

                # Send the request to API no 1
                files = {"audio_file": (audio_file.filename, audio_file.file, audio_file.content_type)}
                response = requests.post(vc_service_url, headers=headers, files=files, data=data)

                if response.status_code == 200:
                    # Return the response from API no 1
                    return FileResponse(
                        response.content,
                        media_type=response.headers["Content-Type"],
                        filename="generated_vc_audio.wav",
                    )
                else:
                    raise HTTPException(status_code=response.status_code, detail=response.text)

        except ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="JWT token has expired. Please log in again.")

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid JSON format in the request headers")
