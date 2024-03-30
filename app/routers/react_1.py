from fastapi import HTTPException, Depends, APIRouter, Header, Form, Request, status
import requests
from fastapi.responses import FileResponse
import os
import io
import tempfile

router = APIRouter()

@router.post("/api/ttm_endpoint")
async def text_to_music(request: Request):
    try:
        request_data = await request.json()
        prompt = request_data.get("prompt")
        if prompt is None:
            raise HTTPException(status_code=400, detail="Prompt is missing in the request body")

        authorization = request.headers.get("Authorization")
        if authorization is None:
            raise HTTPException(status_code=401, detail="Authorization header is missing")
        
        parts = authorization.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid Authorization header format")
        
        access_token = parts[1]

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