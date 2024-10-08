import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from typing import Annotated
from models import TokenData, Admin
from admin_database import get_admin

ADMIN_SECRET_KEY = os.environ.get("ADMIN_SECRET_KEY")

if ADMIN_SECRET_KEY is None:
    raise Exception("ADMIN_SECRET_KEY environment variable is not set")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def create_admin_access_token(data: dict, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, ADMIN_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_admin(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, ADMIN_SECRET_KEY, algorithms=[ALGORITHM])
        print('______________payload______________', payload)
        username: str = payload.get("sub")
        print('______________username______________', username)
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        print('______________token_data______________', token_data)
    except JWTError:
        raise credentials_exception
    admin = get_admin(username=token_data.username)
    print('______________admin______________', admin)
    if admin is None:
        raise credentials_exception
    return admin

async def get_current_active_admin(current_admin: Admin = Depends(get_current_admin)):
    if hasattr(current_admin, 'disabled') and current_admin.disabled:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive admin")
    return current_admin
