from typing import Annotated
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from argon2 import PasswordHasher
from config import settings
from database.crud import get_user_by_username

SECRET_KEY = settings.secret_key
ALGORITHM = settings.jwt_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

pwd_hasher = PasswordHasher()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db, service: str):
    auth_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token_payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        username: str = token_payload.get("sub")
        if username is None:
            raise auth_exception
    except JWTError:
        raise auth_exception
    user = get_user_by_username(db, username, service)
    if user is None:
        raise auth_exception
    return user

