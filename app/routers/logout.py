from fastapi import APIRouter, HTTPException,Response, Request


router = APIRouter()


@router.post("/logout", tags=["Logout"])
async def logout(request: Request, response: Response):
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Access token not found")

    response.delete_cookie(key="access_token")
    logout_message = {"message": "Logout successful"}
    print(logout_message)
    return logout_message


