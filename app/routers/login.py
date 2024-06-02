from fastapi import APIRouter, Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordRequestForm
from models import Token
from admin_database import authenticate_admin
from user_database import get_database, authenticate_user
from admin_auth import create_admin_access_token
from user_auth import create_user_access_token
from sqlalchemy.orm import Session
from fastapi.responses import Response
from fastapi.security import OAuth2PasswordRequestForm


router = APIRouter()

#-------------------------------This endpoint is also 200 OK-----------------------------------------------
# @router.post("/login", tags=["Authentication"])
# async def login_for_access_token(
#     form_data: OAuth2PasswordRequestForm = Depends(),
#     db: Session = Depends(get_database)
# ) -> Token:
#     username = form_data.username
#     password = form_data.password

#     # Attempt authentication for both admin and user
#     admin = authenticate_admin(username, password, db=db)
#     user = authenticate_user(username, password, db=db)

#     if admin:
#         access_token = create_admin_access_token(data={"sub": admin.username})
#     elif user:
#         access_token = create_user_access_token(data={"sub": user.username})
#     else:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )

#     return Token(access_token=access_token, token_type="bearer")




#-------------------------------This endpoint is also 200 OK-----------------------------------------------
# class CustomOAuth2PasswordRequestForm(OAuth2PasswordRequestForm):
#     grant_type: str = "password"
#     scope: str = ""
#     client_id: str = ""
#     client_secret: str = ""

# @router.post("/login", tags=["Authentication"])
# async def login_for_access_token(
#     form_data: CustomOAuth2PasswordRequestForm = Depends(),
#     db: Session = Depends(get_database)
# ) -> Token:
#     username = form_data.username
#     password = form_data.password

#     # Attempt authentication for both admin and user
#     admin = authenticate_admin(username, password, db=db)
#     user = authenticate_user(username, password, db=db)

#     if admin:
#         access_token = create_admin_access_token(data={"sub": admin.username})
#     elif user:
#         access_token = create_user_access_token(data={"sub": user.username})
#     else:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )

#     return Token(access_token=access_token, token_type="bearer")



#-------------------------------This endpoint is also 200 OK-----------------------------------------------
# @router.post("/login", tags=["Authentication"])
# async def login_for_access_token(
#     username: str = Form(...),
#     password: str = Form(...),
#     db: Session = Depends(get_database)
# ) -> Token:
#     # Attempt authentication for both admin and user
#     admin = authenticate_admin(username, password, db=db)
#     user = authenticate_user(username, password, db=db)

#     if admin:
#         access_token = create_admin_access_token(data={"sub": admin.username})
#     elif user:
#         access_token = create_user_access_token(data={"sub": user.username})
#     else:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )

#     return Token(access_token=access_token, token_type="bearer")


#-------------------------------This endpoint is also 200 OK-----------------------------------------------
# @router.post("/login", tags=["Admin_Authentication"])
# async def login_for_access_token(
#     username: str = Form(...),
#     password: str = Form(...),
#     db: Session = Depends(get_database)
# ) -> Token:
#     # Attempt authentication for both admin and user
#     admin = authenticate_admin(username, password, db=db)
#     user = authenticate_user(username, password, db=db)

#     if admin:
#         admin_access_token = create_admin_access_token(data={"sub": admin.username})
#         token_type = "Bearer"
#         print("_____________admin_access_token_____________:", admin_access_token)
#         return Token(access_token=admin_access_token, token_type=token_type)
#     elif user:
#         user_access_token = create_user_access_token(data={"sub": user.username})
#         token_type = "Bearer"
#         print("_____________user_access_token_____________:", user_access_token)
#         return Token(access_token=user_access_token, token_type=token_type)
#     else:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "bearer"},
#         )

#-------------------------------This endpoint is also 200 OK-----------------------------------------------
@router.post("/login", tags=["Admin_Authentication"])
async def login_for_access_token(response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_database)) -> Token:
    username = form_data.username
    password = form_data.password

    # Attempt authentication for both admin and user
    admin = authenticate_admin(username, password, db=db)
    user = authenticate_user(username, password, db=db)

    if admin:
        access_token = create_admin_access_token(data={"sub": admin.username})
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="Lax",
            max_age=1800,
            path="/",
            expires=1800,
        )
        return Token(access_token=access_token, token_type="bearer")
    
    elif user:
        access_token = create_user_access_token(data={"sub": user.username})
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="Lax",
            max_age=1800,
            path="/",
            expires=1800,
        )
        return Token(access_token=access_token, token_type="bearer")
    
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )