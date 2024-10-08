# # # from fastapi import HTTPException, APIRouter, Request
# # # import requests
# # # from fastapi.responses import FileResponse
# # # import tempfile

# # # router = APIRouter()

# # # # @router.post("/api/ttm_endpoint")
# # # # async def text_to_music(request: Request):
# # # #     try:
# # # #         request_data = await request.json()
# # # #         prompt = request_data.get("prompt")
# # # #         if prompt is None:
# # # #             raise HTTPException(status_code=400, detail="Prompt is missing in the request body")

# # # #         authorization = request.headers.get("Authorization")
# # # #         if authorization is None:
# # # #             raise HTTPException(status_code=401, detail="Authorization header is missing")
        
# # # #         parts = authorization.split()
# # # #         if len(parts) != 2 or parts[0].lower() != "bearer":
# # # #             raise HTTPException(status_code=401, detail="Invalid Authorization header format")
        
# # # #         access_token = parts[1]

# # # #         data = {
# # # #             "prompt": prompt
# # # #         }

# # # #         ttm_url = "http://149.11.242.18:14094/ttm_service"  # Adjust the URL as needed
# # # #         headers = {
# # # #             "Accept": "audio/wav",  # Specify the desired audio format
# # # #             "Authorization": f"Bearer {access_token}",
# # # #             "Content-Type": "application/json"
# # # #         }
# # # #         response = requests.post(ttm_url, headers=headers, json=data)

# # # #         if response.status_code == 200:
# # # #             # Create a temporary file to save the audio data
# # # #             with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
# # # #                 temp_file.write(response.content)
# # # #                 temp_file_path = temp_file.name

# # # #             # Return the temporary file using FileResponse
# # # #             return FileResponse(temp_file_path, media_type="audio/wav", filename="generated_audio.wav")
# # # #         else:
# # # #             raise HTTPException(status_code=response.status_code, detail=response.text)

# # # #     except ValueError:
# # # #         raise HTTPException(status_code=400, detail="Invalid JSON format in the request body")


# # # # Define constants for login credentials
# # # LOGIN_USERNAME = "Opentensor@hotmail.com"
# # # LOGIN_PASSWORD = "Opentensor@12345"

# # # # Define a function to check if the user is logged in
# # # def is_user_logged_in():
# # #     # Make a request to the login endpoint to check if the user is logged in
# # #     login_url = "http://149.11.242.18:14094/login"  # Adjust the URL as needed
# # #     login_payload = {
# # #         "username": LOGIN_USERNAME,
# # #         "password": LOGIN_PASSWORD
# # #     }
# # #     login_headers = {
# # #         "accept": "application/json",
# # #         "Content-Type": "application/x-www-form-urlencoded"
# # #     }
# # #     login_response = requests.post(login_url, headers=login_headers, data=login_payload)

# # #     if login_response.status_code == 200:
# # #         # User is logged in, return True
# # #         return True
# # #     else:
# # #         # User is not logged in, return False
# # #         return False

# # # Define a function to log in the user
# # def login_user():
# #     # Make a request to the login endpoint to log in the user
# #     login_url = "http://149.11.242.18:14094/login"  # Adjust the URL as needed
# #     login_payload = {
# #         "username": LOGIN_USERNAME,
# #         "password": LOGIN_PASSWORD
# #     }
# #     login_headers = {
# #         "accept": "application/json",
# #         "Content-Type": "application/x-www-form-urlencoded"
# #     }
# #     login_response = requests.post(login_url, headers=login_headers, data=login_payload)

# #     if login_response.status_code == 200:
# #         # Login successful
# #         return True
# #     else:
# #         # Login failed
# #         return False

# # # @router.post("/api/ttm_endpoint")
# # # async def text_to_music(request: Request):
# # #     try:
# # #         request_data = await request.json()
# # #         prompt = request_data.get("prompt")
# # #         if prompt is None:
# # #             raise HTTPException(status_code=400, detail="Prompt is missing in the request body")

# # #         # Check if the user is logged in
# # #         if not is_user_logged_in():
# # #             # User is not logged in, try to log in
# # #             login_success = login_user()
# # #             if not login_success:
# # #                 raise HTTPException(status_code=401, detail="Login failed. User is not logged in.")

# # #         # Proceed with generating audio data
# # #         access_token = "your_access_token_here"  # Placeholder for the actual access token

# # #         data = {
# # #             "prompt": prompt
# # #         }

# # #         ttm_url = "http://149.11.242.18:14094/ttm_service"  # Adjust the URL as needed
# # #         headers = {
# # #             "Accept": "audio/wav",  # Specify the desired audio format
# # #             "Authorization": f"Bearer {access_token}",
# # #             "Content-Type": "application/json"
# # #         }
# # #         response = requests.post(ttm_url, headers=headers, json=data)

# # #         if response.status_code == 200:
# # #             # Create a temporary file to save the audio data
# # #             with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
# # #                 temp_file.write(response.content)
# # #                 temp_file_path = temp_file.name

# # #             # Return the temporary file using FileResponse
# # #             return FileResponse(temp_file_path, media_type="audio/wav", filename="generated_audio.wav")
# # #         else:
# # #             raise HTTPException(status_code=response.status_code, detail=response.text)

# # #     except ValueError:
# # #         raise HTTPException(status_code=400, detail="Invalid JSON format in the request body")



# from fastapi import HTTPException, APIRouter, Request, Header, Depends, Form
# import requests
# from fastapi.responses import FileResponse
# import tempfile
# import os
# import jwt
# from sqlalchemy.orm import Session
# from models import React_User, Email_User
# from sqlalchemy.orm import sessionmaker, declarative_base
# from sqlalchemy import create_engine
# from typing import Generator
# from jwt.exceptions import ExpiredSignatureError  # Import the ExpiredSignatureError
# from fastapi import UploadFile, File
# from typing import Optional
# import asyncio
# import logging


# router = APIRouter()

# # 

# # Get the database URL from the environment variable
# DATABASE_URL = os.environ.get("DATABASE_URL")

# if DATABASE_URL is None:
#     raise Exception("DATABASE_URL environment variable is not set")

# GOOGLE_EMAIL_LOGIN_SECRET_KEY = os.environ.get("GOOGLE_EMAIL_LOGIN_SECRET_KEY")
# if GOOGLE_EMAIL_LOGIN_SECRET_KEY is None:
#     raise Exception("GOOGLE_EMAIL_LOGIN_SECRET_KEY environment variable is not set")

# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 100000000000000000000000

# # Create the SQLAlchemy engine
# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# # SQLAlchemy models
# Base = declarative_base()

# def initialize_database():
#     from models import Base
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


# # # Define constants for login credentials
# # LOGIN_USERNAME = "Opentensor@hotmail.com"
# # LOGIN_PASSWORD = "Opentensor@123"

# # # Define a function to log in the user and get the access token
# # def login_user():
# #     # Make a request to the login endpoint to log in the user
# #     login_url = "http://38.80.122.248:40337/login"  # Adjust the URL as needed
# #     login_payload = {
# #         "username": LOGIN_USERNAME,
# #         "password": LOGIN_PASSWORD
# #     }
# #     login_headers = {
# #         "accept": "application/json",
# #         "Content-Type": "application/x-www-form-urlencoded"
# #     }
# #     login_response = requests.post(login_url, headers=login_headers, data=login_payload)

# #     if login_response.status_code == 200:
# #         # Login successful, extract and return the access token
# #         response_data = login_response.json()
# #         access_token = response_data.get("access_token")
# #         return access_token
# #     else:
# #         # Login failed
# #         return None

# # # @router.post("/api/ttm_endpoint")
# # # async def text_to_music(request: Request):
# # #     try:
# # #         request_data = await request.json()
# # #         prompt = request_data.get("prompt")
# # #         if prompt is None:
# # #             raise HTTPException(status_code=400, detail="Prompt is missing in the request body")
        
# # #         # Log in the user and get the access token
# # #         access_token = login_user()

# # #         # Proceed with generating audio data using the obtained access token
# # #         data = {
# # #             "prompt": prompt
# # #         }

# # #         ttm_url = "http://38.80.122.248:40337/ttm_service"  # Adjust the URL as needed
# # #         headers = {
# # #             "Accept": "audio/wav",  # Specify the desired audio format
# # #             "Authorization": f"Bearer {access_token}",
# # #             "Content-Type": "application/json"
# # #         }
# # #         response = requests.post(ttm_url, headers=headers, json=data)

# # #         if response.status_code == 200:
# # #             # Create a temporary file to save the audio data
# # #             with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
# # #                 temp_file.write(response.content)
# # #                 temp_file_path = temp_file.name

# # #             # Return the temporary file using FileResponse
# # #             return FileResponse(temp_file_path, media_type="audio/wav", filename="generated_audio.wav")
# # #         else:
# # #             raise HTTPException(status_code=response.status_code, detail=response.text)

# # #     except ValueError:
# # #         raise HTTPException(status_code=400, detail="Invalid JSON format in the request body")


# # @router.post("/api/tts_endpoint")
# # async def text_to_speech(request: Request, authorization: str = Header(None), db: Session = Depends(get_database))  -> FileResponse:
# #     try:
# #         # Extract the request data
# #         request_data = await request.json()
# #         print("________________request_data________________", request_data)
# #         prompt = request_data.get("prompt")
# #         print("________________prompt________________", prompt)
        
# #         if prompt is None:
# #             print("Prompt is missing in the request body.")
# #             raise HTTPException(status_code=400, detail="Prompt is missing in the request body.")

# #         # Check if the Authorization header is present
# #         if authorization is None:
# #             print("Authorization header is missing.")
# #             raise HTTPException(status_code=401, detail="Authorization header is missing.")
        
# #         # Extract the token from the Authorization header
# #         token = authorization.split(" ")[1]  # Assuming the header format is "Bearer <token>"
        
# #         try:
# #             # Decode and verify the JWT token
# #             decoded_token = jwt.decode(token, GOOGLE_EMAIL_LOGIN_SECRET_KEY, algorithms=[ALGORITHM])
# #             print("________________decoded_token________________", decoded_token)

# #             email = decoded_token.get("sub")  # Assuming "sub" contains the email address
# #             print("________________email________________", email)
            
# #             # Query the database based on the email to get user data from React_User and Email_User
# #             react_user = db.query(React_User).filter(React_User.email == email).first()
# #             email_user = db.query(Email_User).filter(Email_User.email == email).first()
# #             print("_______________user details in jwt token (React_User)___________" , react_user)
# #             print("_______________user details in jwt token (Email_User)___________" , email_user)

# #             # If the user is not registered in either React_User or Email_User, raise an exception
# #             if not react_user and not email_user:
# #                 raise HTTPException(status_code=401, detail="___________User is not registered___________")
            
# #             else:
# #                 # Log in the user and get the access token
# #                 access_token = login_user()
# #                 print("_______________access_token___________" , access_token)

# #                 data = {
# #                     "prompt": prompt
# #                 }

# #                 ttm_url = "http://38.80.122.248:40337/tts_service"  # Adjust the URL as needed
# #                 headers = {
# #                     "Accept": "audio/wav",  # Specify the desired audio format
# #                     "Authorization": f"Bearer {access_token}",
# #                     "Content-Type": "application/json"
# #                 }

# #                 response = requests.post(ttm_url, headers=headers, json=data)

# #                 if response.status_code == 200:
# #                     # Create a temporary file to save the audio data
# #                     with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
# #                         temp_file.write(response.content)
# #                         temp_file_path = temp_file.name

# #                     # Return the temporary file using FileResponse
# #                     return FileResponse(temp_file_path, media_type="audio/wav", filename="generated_tts_audio.wav")
# #                 else:
# #                     raise HTTPException(status_code=response.status_code, detail=response.text)

# #         except ExpiredSignatureError:
# #             raise HTTPException(status_code=401, detail="JWT token has expired. Please log in again.")

# #     except ValueError:
# #         raise HTTPException(status_code=400, detail="Invalid JSON format in the request headers")



# # @router.post("/api/ttm_endpoint")
# # async def text_to_music(request: Request, authorization: str = Header(None), db: Session = Depends(get_database))  -> FileResponse:
# #     try:
# #         # Extract the request data
# #         request_data = await request.json()
# #         print("________________request_data________________", request_data)
# #         prompt = request_data.get("prompt")
# #         print("________________prompt________________", prompt)
        
# #         if prompt is None:
# #             print("Prompt is missing in the request body.")
# #             raise HTTPException(status_code=400, detail="Prompt is missing in the request body.")

# #         # Check if the Authorization header is present
# #         if authorization is None:
# #             print("Authorization header is missing.")
# #             raise HTTPException(status_code=401, detail="Authorization header is missing.")
        
# #         # Extract the token from the Authorization header
# #         token = authorization.split(" ")[1]  # Assuming the header format is "Bearer <token>"
        
# #         try:
# #             # Decode and verify the JWT token
# #             decoded_token = jwt.decode(token, GOOGLE_EMAIL_LOGIN_SECRET_KEY, algorithms=[ALGORITHM])
# #             print("________________decoded_token________________", decoded_token)

# #             email = decoded_token.get("sub")  # Assuming "sub" contains the email address
# #             print("________________email________________", email)
            
# #             # Query the database based on the email to get user data from React_User and Email_User
# #             react_user = db.query(React_User).filter(React_User.email == email).first()
# #             email_user = db.query(Email_User).filter(Email_User.email == email).first()
# #             print("_______________user details in jwt token (React_User)___________" , react_user)
# #             print("_______________user details in jwt token (Email_User)___________" , email_user)

# #             # If the user is not registered in either React_User or Email_User, raise an exception
# #             if not react_user and not email_user:
# #                 raise HTTPException(status_code=401, detail="___________User is not registered___________")
            
# #             else:
# #                 # Log in the user and get the access token
# #                 access_token = login_user()
# #                 print("_______________access_token___________" , access_token)

# #                 data = {
# #                     "prompt": prompt
# #                 }

# #                 ttm_url = "http://38.80.122.248:40337/ttm_service"  # Adjust the URL as needed
# #                 headers = {
# #                     "Accept": "audio/wav",  # Specify the desired audio format
# #                     "Authorization": f"Bearer {access_token}",
# #                     "Content-Type": "application/json"
# #                 }

# #                 response = requests.post(ttm_url, headers=headers, json=data)

# #                 if response.status_code == 200:
# #                     # Create a temporary file to save the audio data
# #                     with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
# #                         temp_file.write(response.content)
# #                         temp_file_path = temp_file.name

# #                     # Return the temporary file using FileResponse
# #                     return FileResponse(temp_file_path, media_type="audio/wav", filename="generated_ttm_audio.wav")
# #                 else:
# #                     raise HTTPException(status_code=response.status_code, detail=response.text)

# #         except ExpiredSignatureError:
# #             raise HTTPException(status_code=401, detail="JWT token has expired. Please log in again.")

# #     except ValueError:
# #         raise HTTPException(status_code=400, detail="Invalid JSON format in the request headers")
    

    

# # # @router.post("/api/vc_endpoint")
# # # async def voice_clone(
# # #     request: Request,
# # #     audio_file: UploadFile = File(...),
# # #     authorization: str = Header(None),
# # #     db: Session = Depends(get_database)
# # # ) -> FileResponse:
# # #     try:
# # #         # Extract the request data
# # #         request_data = await request.json()
# # #         print("________________request_data________________", request_data)
# # #         prompt = request_data.get("prompt")
# # #         print("________________prompt________________", prompt)

# # #         # Validate prompt
# # #         if not prompt:
# # #             raise HTTPException(status_code=400, detail="Prompt is missing in the request body.")

# # #         # Check if the Authorization header is present
# # #         if authorization is None:
# # #             raise HTTPException(status_code=401, detail="Authorization header is missing.")

# # #         # Extract the token from the Authorization header
# # #         token = authorization.split(" ")[1]  # Assuming the header format is "Bearer <token>"

# # #         try:
# # #             # Decode and verify the JWT token
# # #             decoded_token = jwt.decode(token, GOOGLE_EMAIL_LOGIN_SECRET_KEY, algorithms=[ALGORITHM])
# # #             email = decoded_token.get("sub")  # Assuming "sub" contains the email address

# # #             # Query the database based on the email to get user data from React_User and Email_User
# # #             react_user = db.query(React_User).filter(React_User.email == email).first()
# # #             email_user = db.query(Email_User).filter(Email_User.email == email).first()

# # #             # If the user is not registered in either React_User or Email_User, raise an exception
# # #             if not react_user and not email_user:
# # #                 raise HTTPException(status_code=401, detail="User is not registered.")

# # #             else:
# # #                 # Log in the user and get the access token
# # #                 access_token = login_user()

# # #                 data = {
# # #                     "prompt": prompt
# # #                 }

# # #                 # Adjust the URL to point to API no 1 (/vc_service)
# # #                 vc_service_url = "http://38.80.122.248:40337/vc_service"  # Adjust the URL as needed
# # #                 headers = {
# # #                     "Accept": "audio/wav",  # Specify the desired audio format
# # #                     "Authorization": f"Bearer {access_token}",
# # #                     "Content-Type": "multipart/form-data"
# # #                 }

# # #                 # Send the request to API no 1
# # #                 files = {"audio_file": (audio_file.filename, audio_file.file, audio_file.content_type)}
# # #                 response = requests.post(vc_service_url, headers=headers, files=files, data=data)

# # #                 if response.status_code == 200:
# # #                     # Return the response from API no 1
# # #                     return FileResponse(
# # #                         response.content,
# # #                         media_type=response.headers["Content-Type"],
# # #                         filename="generated_vc_audio.wav",
# # #                     )
# # #                 else:
# # #                     raise HTTPException(status_code=response.status_code, detail=response.text)

# # #         except ExpiredSignatureError:
# # #             raise HTTPException(status_code=401, detail="JWT token has expired. Please log in again.")

# # #     except ValueError:
# # #         raise HTTPException(status_code=400, detail="Invalid JSON format in the request headers")



# # @router.post("/api/vc_endpoint")
# # async def voice_clone(
# #     audio_file: UploadFile = File(...),
# #     prompt: str = Form(...),
# #     authorization: str = Header(None),
# #     db: Session = Depends(get_database)
# # ) -> FileResponse:
# #     try:
# #         # Validate prompt
# #         if not prompt:
# #             raise HTTPException(status_code=400, detail="Prompt is missing in the request body.")

# #         # Check if the Authorization header is present
# #         if authorization is None:
# #             raise HTTPException(status_code=401, detail="Authorization header is missing.")

# #         # Extract the token from the Authorization header
# #         token = authorization.split(" ")[1]  # Assuming the header format is "Bearer <token>"

# #         try:
# #             # Decode and verify the JWT token
# #             decoded_token = jwt.decode(token, GOOGLE_EMAIL_LOGIN_SECRET_KEY, algorithms=[ALGORITHM])
# #             email = decoded_token.get("sub")  # Assuming "sub" contains the email address

# #             # Query the database based on the email to get user data from React_User and Email_User
# #             react_user = db.query(React_User).filter(React_User.email == email).first()
# #             email_user = db.query(Email_User).filter(Email_User.email == email).first()

# #             # If the user is not registered in either React_User or Email_User, raise an exception
# #             if not react_user and not email_user:
# #                 raise HTTPException(status_code=401, detail="User is not registered.")

# #             else:
# #                 # Log in the user and get the access token
# #                 access_token = login_user()

# #                 data = {
# #                     "prompt": prompt
# #                 }

# #                 # Adjust the URL to point to API no 1 (/vc_service)
# #                 vc_service_url = "http://38.80.122.248:40337/vc_service"  # Adjust the URL as needed
# #                 headers = {
# #                     "Authorization": f"Bearer {access_token}"
# #                 }

# #                 # Send the request to API no 1
# #                 files = {"audio_file": ("audio_file.wav", audio_file.file, "audio/wav")}
# #                 response = requests.post(vc_service_url, headers=headers, files=files, data=data)

# #                 if response.status_code == 200:
# #                     # Return the response from API no 1 and create a temporary file to save the audio data
# #                     with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
# #                         temp_file.write(response.content)
# #                         temp_file_path = temp_file.name

# #                         # Return the response to the client
# #                         return FileResponse(temp_file_path, media_type="audio/wav", filename="generated_vc_audio.wav")
# #                 else:
# #                     raise HTTPException(status_code=response.status_code, detail=response.text)

# #         except ExpiredSignatureError:
# #             raise HTTPException(status_code=401, detail="JWT token has expired. Please log in again.")

# #     except ValueError:
# #         raise HTTPException(status_code=400, detail="Invalid JSON format in the request headers")


# # from fastapi import HTTPException, APIRouter, Request, Header, Depends, Form
# # import requests
# # from fastapi.responses import FileResponse
# # import tempfile
# # import os
# # import jwt
# # from sqlalchemy.orm import Session
# # from models import React_User, Email_User
# # from sqlalchemy.orm import sessionmaker, declarative_base
# # from sqlalchemy import create_engine
# # from typing import Generator, Optional
# # from jwt.exceptions import ExpiredSignatureError  # Import the ExpiredSignatureError
# # from fastapi import UploadFile, File
# # import asyncio


# # router = APIRouter()

# # # 

# # # Get the database URL from the environment variable
# # DATABASE_URL = os.environ.get("DATABASE_URL")

# # if DATABASE_URL is None:
# #     raise Exception("DATABASE_URL environment variable is not set")

# # GOOGLE_EMAIL_LOGIN_SECRET_KEY = os.environ.get("GOOGLE_EMAIL_LOGIN_SECRET_KEY")
# # if GOOGLE_EMAIL_LOGIN_SECRET_KEY is None:
# #     raise Exception("GOOGLE_EMAIL_LOGIN_SECRET_KEY environment variable is not set")

# # ALGORITHM = "HS256"
# # ACCESS_TOKEN_EXPIRE_MINUTES = 30

# # # Create the SQLAlchemy engine
# # engine = create_engine(DATABASE_URL)
# # SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# # # SQLAlchemy models
# # Base = declarative_base()

# # def initialize_database():
# #     from models import Base
# #     Base.metadata.create_all(bind=engine)
# #     print("Database initialized successfully.")

# # # Dependency to get the database session
# # def get_database() -> Generator[Session, None, None]:
# #     # Provide a database session to use within the request
# #     db = SessionLocal()
# #     try:
# #         yield db
# #     finally:
# #         db.close()


# # async def login_user(username: str, password: str, login_url: str) -> str:
# #     login_payload = {
# #         "username": username,
# #         "password": password
# #     }
# #     login_headers = {
# #         "accept": "application/json",
# #         "Content-Type": "application/x-www-form-urlencoded"
# #     }
# #     login_response = requests.post(login_url, headers=login_headers, data=login_payload)

# #     if login_response.status_code == 200:
# #         # Login successful, return the access token
# #         response_data = login_response.json()
# #         access_token = response_data.get("access_token")
# #         return access_token
# #     else:
# #         # Login failed
# #         return None

# # async def send_request(url: str, data: dict, headers: dict) -> requests.Response:
# #     # Send a POST request to the specified URL with data and headers
# #     return requests.post(url, json=data, headers=headers)


# # @router.post("/api/tts_endpoint")
# # async def text_to_speech(request: Request, authorization: Optional[str] = Header(None), db: Session = Depends(get_database)) -> FileResponse:
# #     try:
# #         # Extract the request data
# #         request_data = await request.json()
# #         prompt = request_data.get("prompt")
# #         if prompt is None:
# #             raise HTTPException(status_code=400, detail="Prompt is missing in the request body.")

# #         # Check if the Authorization header is present
# #         if authorization is None:
# #             raise HTTPException(status_code=401, detail="Authorization header is missing.")
        
# #         # Extract the token from the Authorization header
# #         token = authorization.split(" ")[1]  # Assuming the header format is "Bearer <token>"
        
# #         try:
# #             # Decode and verify the JWT token
# #             decoded_token = jwt.decode(token, GOOGLE_EMAIL_LOGIN_SECRET_KEY, algorithms=[ALGORITHM])
# #             email = decoded_token.get("sub")

# #             # Query the database based on the email to get user data from React_User and Email_User
# #             react_user = db.query(React_User).filter(React_User.email == email).first()
# #             email_user = db.query(Email_User).filter(Email_User.email == email).first()

# #             # If the user is not registered in either React_User or Email_User, raise an exception
# #             if not react_user and not email_user:
# #                 raise HTTPException(status_code=401, detail="User is not registered.")
            
# #             else:
# #                 # Define the login URLs and credentials
# #                 LOGIN_URL_1 = "http://38.80.122.166:40440/login"
# #                 LOGIN_URL_2 = "http://79.116.48.205:24942/login"
# #                 LOGIN_USERNAME_1 = "Opentensor@hotmail.com_val3"
# #                 LOGIN_PASSWORD_1 = "Opentensor@12345"
# #                 LOGIN_USERNAME_2 = "Opentensor@hotmail.com_val4"
# #                 LOGIN_PASSWORD_2 = "Opentensor@12345"

# #                 # Log in the user asynchronously using the appropriate credentials and login URLs
# #                 access_token_1 = await login_user(LOGIN_USERNAME_1, LOGIN_PASSWORD_1, LOGIN_URL_1)
# #                 access_token_2 = await login_user(LOGIN_USERNAME_2, LOGIN_PASSWORD_2, LOGIN_URL_2)

# #                 # Define the data and headers for the requests to the text-to-speech service
# #                 data = {"prompt": prompt}
# #                 headers_1 = {"Authorization": f"Bearer {access_token_1}", "Content-Type": "application/json"}
# #                 headers_2 = {"Authorization": f"Bearer {access_token_2}", "Content-Type": "application/json"}

# #                 # Define the URLs for the text-to-speech service
# #                 TTS_URL_1 = "http://38.80.122.166:40440/tts_service"
# #                 TTS_URL_2 = "http://79.116.48.205:24942/tts_service"

# #                 # Send request to the first text-to-speech URL
# #                 response_1 = await send_request(TTS_URL_1, data, headers_1)

# #                 if response_1.status_code == 200:
# #                     # Create a temporary file to save the audio data
# #                     with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
# #                         temp_file.write(response_1.content)
# #                         temp_file_path = temp_file.name

# #                     # Return the temporary file using FileResponse
# #                     return FileResponse(temp_file_path, media_type="audio/wav", filename="generated_tts_audio.wav")

# #                 else:
# #                     # Send request to the second text-to-speech URL if the first one fails
# #                     response_2 = await send_request(TTS_URL_2, data, headers_2)

# #                     if response_2.status_code == 200:
# #                         # Create a temporary file to save the audio data
# #                         with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
# #                             temp_file.write(response_2.content)
# #                             temp_file_path = temp_file.name

# #                         # Return the temporary file using FileResponse
# #                         return FileResponse(temp_file_path, media_type="audio/wav", filename="generated_tts_audio.wav")
# #                     else:
# #                         raise HTTPException(status_code=response_2.status_code, detail=response_2.text)

# #         except ExpiredSignatureError:
# #             raise HTTPException(status_code=401, detail="JWT token has expired. Please log in again.")

# #     except ValueError:
# #         raise HTTPException(status_code=400, detail="Invalid JSON format in the request headers")
    

# ####################################################





# from requests.adapters import HTTPAdapter
# from requests.packages.urllib3.util.retry import Retry

# # Define constants for login credentials and URLs
# LOGIN_CREDENTIALS = [
#     {"url": "http://89.37.121.214:44107", "username": "Opentensor@hotmail.com_val1", "password": "Opentensor@12345"},
#     {"url": "http://149.11.242.18:14428", "username": "Opentensor@hotmail.com_val2", "password": "Opentensor@12345"}
# ]

# def create_session():
#     session = requests.Session()
#     retries = Retry(total=1, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
#     adapter = HTTPAdapter(max_retries=retries)
#     session.mount('http://', adapter)
#     session.mount('https://', adapter)
#     return session

# def login_user(credentials):
#     session = create_session()
#     index = 0  # Start with the first credential

#     while index < len(credentials):
#         credential = credentials[index]
#         try:
#             login_url = f"{credential['url']}/login"
#             login_payload = {
#                 "username": credential["username"],
#                 "password": credential["password"]
#             }
#             login_headers = {
#                 "accept": "application/json",
#                 "Content-Type": "application/x-www-form-urlencoded"
#             }
#             login_response = session.post(login_url, headers=login_headers, data=login_payload, timeout=10)

#             if login_response.status_code == 200:
#                 response_data = login_response.json()
#                 access_token = response_data.get("access_token")
#                 return access_token, credential['url']  # Return the access token and corresponding URL

#         except requests.exceptions.RequestException as e:
#             logging.error(f"Error occurred while logging in: {e}")

#         # Move to the next credential
#         index += 1

#     # If all attempts fail, raise an exception or handle it as needed
#     raise HTTPException(status_code=401, detail="Login failed for all credentials")


# @router.post("/api/tts_endpoint")
# async def text_to_speech(request: Request, authorization: str = Header(None), db: Session = Depends(get_database)) -> FileResponse:
#     try:
#         # Extract the request data
#         request_data = await request.json()
#         prompt = request_data.get("prompt")
        
#         if prompt is None:
#             raise HTTPException(status_code=400, detail="Prompt is missing in the request body.")

#         # Check if the Authorization header is present
#         if authorization is None:
#             raise HTTPException(status_code=401, detail="Authorization header is missing.")
        
#         # Extract the token from the Authorization header
#         token = authorization.split(" ")[1]  # Assuming the header format is "Bearer <token>"
        
#         try:
#             # Decode and verify the JWT token
#             decoded_token = jwt.decode(token, GOOGLE_EMAIL_LOGIN_SECRET_KEY, algorithms=[ALGORITHM])
#             email = decoded_token.get("sub")  # Assuming "sub" contains the email address
            
#             # Query the database based on the email to get user data from React_User and Email_User
#             react_user = db.query(React_User).filter(React_User.email == email).first()
#             email_user = db.query(Email_User).filter(Email_User.email == email).first()

#             # Your logic for checking user existence and authorization goes here

#             # If the user is not registered in either React_User or Email_User, raise an exception
#             if not react_user and not email_user:
#                 raise HTTPException(status_code=401, detail="User is not registered")
            
#             # Log in the user and get the access token and corresponding URL
#             access_token= login_url = login_user(LOGIN_CREDENTIALS)
#             data = {"prompt": prompt}

#             tts_url = f"{login_url}/tts_service"  # Construct the TTS URL based on successful login URL
#             headers = {
#                 "Accept": "audio/wav",
#                 "Authorization": f"Bearer {access_token}",
#                 "Content-Type": "application/json"
#             }

#             response = requests.post(tts_url, headers=headers, json=data)

#             if response.status_code == 200:
#                 # Create a temporary file to save the audio data
#                 with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
#                     temp_file.write(response.content)
#                     temp_file_path = temp_file.name

#                 # Return the temporary file using FileResponse
#                 return FileResponse(temp_file_path, media_type="audio/wav", filename="generated_tts_audio.wav")
#             else:
#                 raise HTTPException(status_code=response.status_code, detail=response.text)

#         except ExpiredSignatureError:
#             raise HTTPException(status_code=401, detail="JWT token has expired. Please log in again.")

#     except ValueError:
#         raise HTTPException(status_code=400, detail="Invalid JSON format in the request headers")
    



# @router.post("/api/ttm_endpoint")
# async def text_to_music(request: Request, authorization: Optional[str] = Header(None), db: Session = Depends(get_database)):
#     try:
#         # Extract the request data
#         request_data = await request.json()
#         prompt = request_data.get("prompt")
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
#             access_token, login_url = login_user(LOGIN_CREDENTIALS)
#             data = {"prompt": prompt}

#             ttm_url = f"{login_url}/ttm_service"  # Construct the TTM URL based on successful login URL
#             headers = {
#                 "Accept": "audio/wav",
#                 "Authorization": f"Bearer {access_token}",
#                 "Content-Type": "application/json"
#             }

#             response = requests.post(ttm_url, headers=headers, json=data)

#             if response.status_code == 200:
#                 # Create a temporary file to save the audio data
#                 with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
#                     temp_file.write(response.content)
#                     temp_file_path = temp_file.name

#                 # Return the temporary file using FileResponse
#                 return FileResponse(temp_file_path, media_type="audio/wav", filename="generated_ttm_audio.wav")
#             else:
#                 raise HTTPException(status_code=response.status_code, detail=response.text)

#         except ExpiredSignatureError:
#             raise HTTPException(status_code=401, detail="JWT token has expired. Please log in again.")

#     except ValueError:
#         raise HTTPException(status_code=400, detail="Invalid JSON format in the request headers")




# @router.post("/api/vc_endpoint")
# async def voice_clone(
#     audio_file: UploadFile = File(...),
#     prompt: str = Form(...),
#     authorization: str = Header(None),
#     db: Session = Depends(get_database)
# ) -> FileResponse:
#     try:
#         # Validate prompt
#         if not prompt:
#             raise HTTPException(status_code=400, detail="Prompt is missing in the request body.")

#         # Check if the Authorization header is present
#         if authorization is None:
#             raise HTTPException(status_code=401, detail="Authorization header is missing.")

#         # Extract the token from the Authorization header
#         token = authorization.split(" ")[1]  # Assuming the header format is "Bearer <token>"

#         try:
#             # Decode and verify the JWT token
#             decoded_token = jwt.decode(token, GOOGLE_EMAIL_LOGIN_SECRET_KEY, algorithms=[ALGORITHM])
#             email = decoded_token.get("sub")  # Assuming "sub" contains the email address

#             # Query the database based on the email to get user data from React_User and Email_User
#             react_user = db.query(React_User).filter(React_User.email == email).first()
#             email_user = db.query(Email_User).filter(Email_User.email == email).first()

#             # If the user is not registered in either React_User or Email_User, raise an exception
#             if not react_user and not email_user:
#                 raise HTTPException(status_code=401, detail="User is not registered.")

#             # Log in the user and get the access token
#             access_token, login_url = login_user(LOGIN_CREDENTIALS)

#             data = {
#                 "prompt": prompt
#             }

#             vc_url = f"{login_url}/vc_service"  # Construct the VC URL based on successful login URL
#             headers = {"Authorization": f"Bearer {access_token}"}

#             response = requests.post(vc_url, headers=headers, json=data)

#             if response.status_code == 200:
#                 # Create a temporary file to save the audio data
#                 with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
#                     temp_file.write(response.content)
#                     temp_file_path = temp_file.name
#                 return FileResponse(temp_file_path, media_type="audio/wav", filename="generated_vc_audio.wav")
#             else:
#                 raise HTTPException(status_code=response.status_code, detail=response.text)

#         except ExpiredSignatureError:
#             raise HTTPException(status_code=401, detail="JWT token has expired. Please log in again.")

#     except ValueError:
#         raise HTTPException(status_code=400, detail="Invalid JSON format in the request headers")


