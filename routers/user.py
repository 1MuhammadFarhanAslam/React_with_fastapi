
from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, File
from user_database import get_user, verify_user_credentials, update_user_password, get_database
import logging
from mimetypes import guess_type
from fastapi import Depends
from datetime import datetime
from models import User, User
from user_auth import get_current_active_user
import re
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/change_password", response_model=dict)
async def change_user_password(
    username: str = Form(...),
    current_password: str = Form(...),
    new_password: str = Form(..., min_length=8, max_length=16, regex="^[a-zA-Z0-9!@#$%^&*()_+{}\[\]:;<>,.?/~\\-=|\\\\]+$"),
    confirm_new_password: str = Form(...),
    current_active_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)  # Dependency to provide the session
):
    try:
        # Validate that all required fields are provided
        if not username or not current_password or not new_password or not confirm_new_password:
            raise HTTPException(status_code=400, detail="All fields are required.")

        # Check if the username exists
        user = get_user(username, db)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Verify the user's current password
        if not verify_user_credentials(username, current_password, db):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Check if the new password and confirm new password match
        if new_password != confirm_new_password:
            raise HTTPException(status_code=400, detail="New password and confirm new password do not match.")

        # Check if the new password is different from the current password
        if current_password == new_password:
            raise HTTPException(status_code=400, detail="New password must be different from the current password.")

        # Additional validation: Check if the new password meets the specified conditions
        if not re.match("^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+$", new_password):
            raise HTTPException(status_code=400, detail="New password must contain at least one uppercase letter, one lowercase letter, one digit, and one special character.")

        # Update the user's password
        updated_user = update_user_password(username, new_password, db)
        if not updated_user:
            raise HTTPException(status_code=500, detail="Failed to update password.")

        return {"message": "Password changed successfully"}

    except HTTPException as e:
        raise e  # Re-raise HTTPException to return specific error response
    except Exception as e:
        # Log the error for debugging
        logging.error(f"Error during password change: {e}")
        # Return a generic error response
        raise HTTPException(status_code=500, detail="Internal Server Error. Check the server logs for more details.")


##########################################################################################################################

# Endpoint for tts_service
@router.post("/tts_service")
async def tts_service(user: User = Depends(get_current_active_user)):
    user_dict = jsonable_encoder(user)  # Convert User object to a dictionary
    print("User details:", user_dict)   # Print the dictionary
    if user.roles:
        role = user.roles[0]
        if user.subscription_end_time and datetime.utcnow() <= user.subscription_end_time and role.tts_enabled == 1:
            print("Congratulations! You have access to Text-to-Speech (TTS) service.")
            return {"message": f"{user.username}! Welcome to the Text-to-Speech service, enjoy your experience!"}
        else:
            print("You do not have access to Text-to-Speech service or subscription is expired.")
            raise HTTPException(status_code=403, detail="Your subscription have expired or you does not have any access to Text-to-Speech service")
    else:
        print("User does not have any roles assigned.")
        raise HTTPException(status_code=403, detail="User does not have any roles assigned")


# Endpoint for ttm_service
@router.post("/ttm_service")
async def ttm_service(user: User = Depends(get_current_active_user)):
    user_dict = jsonable_encoder(user)
    print("User details:", user_dict)
    if user.roles:
        role = user.roles[0]
        if user.subscription_end_time and datetime.utcnow() <= user.subscription_end_time and role.ttm_enabled == 1:
            print("Congratulations! You have access to Text-to-Music (TTM) service.")
            return {"message": f"{user.username}! Welcome to the Text-to-Music service, enjoy your experience!"}
        else:
            print("You do not have access to Text-to-Music service or subscription is expired.")
            raise HTTPException(status_code=403, detail="Your subscription have been expired or you does not have any access to Text-to-Music service")
    else:
        print("You do not have any roles assigned.")
        raise HTTPException(status_code=403, detail="Your does not have any roles assigned")

from fastapi import UploadFile, File


@router.post("/vc_service")
async def vc_service(
    user: User = Depends(get_current_active_user),
    audio_file: UploadFile = File(...)
):
    user_dict = jsonable_encoder(user)
    print("User details:", user_dict)
    
    # Check if the file is an audio file
    allowed_audio_types = ["audio/mpeg", "audio/wav", "audio/mp3"]  # Add more audio MIME types if needed
    file_type = guess_type(audio_file.filename)[0]
    
    if file_type not in allowed_audio_types:
        raise HTTPException(status_code=400, detail="Uploaded file must be an audio file.")
    
    if user.roles:
        role = user.roles[0]
        if user.subscription_end_time and datetime.utcnow() <= user.subscription_end_time and role.vc_enabled == 1:
            print("Congratulations! You have access to Voice Clone (VC) service.")
            return {"message": f"{user.username}! Welcome to the Voice Clone service. Enjoy your experience!"}
        else:
            print("You do not have access to Voice Clone service or subscription is expired.")
            raise HTTPException(status_code=403, detail="Your subscription has expired or you do not have access to the Voice Clone service.")
    else:
        print("You do not have any roles assigned.")
        raise HTTPException(status_code=403, detail="User does not have any roles assigned")

