from fastapi import HTTPException, Depends, APIRouter, Header, Form, Request, status
import requests

router = APIRouter()

@router.post("/api/ttm_endpoint")
async def text_to_music(request: Request):
    try:
        request_data = await request.json()
        print("_______________request_data_______________", request_data)
        prompt = request_data.get("prompt")
        print("_______________prompt_______________", prompt)
        if prompt is None:
            raise HTTPException(status_code=400, detail="Prompt is missing in the request body")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid JSON format in the request body")

    authorization = request.headers.get("Authorization")
    print("_______________authorization_______________", authorization)
    if authorization is None:
        raise HTTPException(status_code=401, detail="Authorization header is missing")
    
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")
    
    access_token = parts[1]
    print("_______________access_token_______________", access_token)

    data = {
        "prompt": prompt
    }
    print("_______________data_______________", data)

    ttm_url = "http://149.11.242.18:14094/ttm_service"  # Adjust the URL as needed
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    print("_______________headers_______________", headers)
    response = requests.post(ttm_url, headers=headers, json=data)

    if response.status_code == 200:
        audio_data = response.json().get("audio_data")
        return {"audio_data": audio_data}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)