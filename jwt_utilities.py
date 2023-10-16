from jose import jwt, JWTError, ExpiredSignatureError
from config import settings
from datetime import datetime, timedelta
from fastapi import HTTPException
import secrets



def encode_jwt(data, service: str, expires_delta: timedelta | None = None, secret_key: str = str(settings.SECRET_KEY)):
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    data.update({"exp": expire})
    data.update({"service": service})
    encoded_jwt = jwt.encode(data, secret_key, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_jwt(token, secret_key: str = str(settings.SECRET_KEY)):
    try:
        token_payload = jwt.decode(token, secret_key, algorithms=settings.JWT_ALGORITHM)
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Expired JWT Token")
    except JWTError:
        raise HTTPException(status_code=400, detail="JWT Decode Error")
    return token_payload
