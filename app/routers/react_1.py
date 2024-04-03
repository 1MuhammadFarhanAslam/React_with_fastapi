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



from fastapi import HTTPException, APIRouter, Request
import requests
from fastapi.responses import FileResponse
import tempfile

router = APIRouter()

# Define constants for login credentials
LOGIN_USERNAME = "Opentensor@hotmail.com"
LOGIN_PASSWORD = "Opentensor@12345"

# Define a function to log in the user and get the access token
def login_user():
    # Make a request to the login endpoint to log in the user
    login_url = "http://149.11.242.18:14094/login"  # Adjust the URL as needed
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

@router.post("/api/ttm_endpoint")
async def text_to_music(request: Request):
    try:
        request_data = await request.json()
        prompt = request_data.get("prompt")
        if prompt is None:
            raise HTTPException(status_code=400, detail="Prompt is missing in the request body")

        # Log in the user and get the access token
        access_token = login_user()

        # Proceed with generating audio data using the obtained access token
        data = {
            "prompt": prompt
        }

        ttm_url = "http://149.11.242.18:14094/ttm_service"  # Adjust the URL as needed
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
            return FileResponse(temp_file_path, media_type="audio/wav", filename="generated_audio.wav")
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid JSON format in the request body")
