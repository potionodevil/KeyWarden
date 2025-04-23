from datetime import datetime, timedelta

from cryptography.hazmat.primitives import hashes
from exceptiongroup import catch
from fastapi import Depends, HTTPException
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
import secrets

SECRET_KEY = secrets.token_urlsafe(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def get_current_user(token: str = Depends(oauth2_scheme)):
    user_data = verify_access_token(token)
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    return user_data

