from jose import jwt, JWTError, ExpiredSignatureError
from config import settings
from datetime import datetime, timedelta
from fastapi import HTTPException

SECRET_KEY = settings.secret_key
ALGORITHM = settings.jwt_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


class JWTToken:
    def __init__(self, payload=None, token: str=None):
        if payload is None:
            payload = {}
        self.secret_key = settings.secret_key
        self.algorithm = settings.jwt_algorithm
        self.payload = payload
        self.token = token
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        if self.payload is None:
            self.payload = {}
        self.payload.update({"exp": expire})

    def encode_jwt(self):
        #expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        #self.payload.update({"exp": expire})
        self.token = jwt.encode(self.payload, self.secret_key, self.algorithm)
        return self.token

    def decode_jwt(self):
        payload = jwt.decode(self.token, self.secret_key, self.algorithm)
        return payload

class JWTUserAccessToken():
    def __init__(self, service: str, user):
        self.payload = {
            "sub": user.username,
            "service": service
        }
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        self.payload.update({"exp": expire})
        self.secret_key = settings.secret_key
        self.algorithm = settings.jwt_algorithm

    def encode_jwt(self):
        return jwt.encode(self.payload, self.secret_key, self.algorithm)


def encode_jwt(data, service: str, expires_delta: timedelta | None = None, secret_key: str = settings.secret_key):
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data.update({"exp": expire})
    data.update({"service": service})
    encoded_jwt = jwt.encode(data, secret_key, algorithm=ALGORITHM)
    return encoded_jwt


def decode_jwt(token, secret_key: str = settings.secret_key):
    try:
        token_payload = jwt.decode(token, secret_key, algorithms=ALGORITHM)
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Expired JWT Token")
    except JWTError:
        raise HTTPException(status_code=400, detail="JWT Decode Error")
    return token_payload
