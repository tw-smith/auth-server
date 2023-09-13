from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends, status, Form, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from database import auth_schemas
from database.crud import get_user_by_email, get_user_by_username, create_user
from db_utils import get_db
from sqlalchemy.orm import Session
from utils import pwd_hasher
from email_utils import VerificationEmail, PasswordResetEmail
from jwt_utilities import decode_jwt, JWTUserAccessToken


router = APIRouter()


class SignupForm:
    def __init__(self,
                 email: str = Form(),
                 username: str = Form(),
                 password: str = Form()):
        self.email = email
        self.username = username
        self.password = password


class PasswordChangeForm:
    def __init__(self,
                 username: str = Form(),
                 old_password: str = Form(),
                 new_password: str = Form()):
        self.username = username
        self.old_password = old_password
        self.new_password = new_password


class PasswordResetRequestForm:
    def __init__(self,
                 email: str = Form()):
        self.email = email


class Token(BaseModel):
    access_token: str
    token_type: str


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup_user(service: str,
                      background_tasks: BackgroundTasks,
                      form_data: Annotated[SignupForm, Depends()],
                      request: Request,
                      db: Session = Depends(get_db)):
    db_user_email = get_user_by_email(db, form_data.email, service)
    db_user_username = get_user_by_username(db, form_data.username, service)
    if db_user_email or db_user_username:
        raise HTTPException(status_code=400, detail="Email or username already registered")
    user = auth_schemas.UserCreate(
        email=form_data.email,
        username=form_data.username,
        password_hash=pwd_hasher.hash(form_data.password)
    )
    user_object = create_user(db=db, user=user, service=service)
    verification_email = VerificationEmail(user_object, service, str(request.url_for('verify_user')))
    background_tasks.add_task(verification_email.send_email)
    #background_tasks.add_task(send_verification_email, user_object, service, request.url_for("verify_user"))
    return {"msg": "user created"}


@router.get("/verify")
async def verify_user(token: str,
                      db: Session = Depends(get_db)):
    #try:
    token_payload = decode_jwt(token)
    #except JWTError:
    #    raise HTTPException(status_code=400, detail="jwt error")
    user = get_user_by_username(db, token_payload['sub'], token_payload['service'])
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid JWT")
    else:
        user.verified = True
        db.commit() #TODO move this to db crud utils?
        return {"msg": "user verified"}


@router.post("/auth", response_model=Token)
async def login_user(service: str,
                     form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                     db: Session = Depends(get_db)):
    user = get_user_by_username(db, form_data.username, service)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Authorisation Error",
                            headers={"WWW-Authenticate": "Bearer"})
    if user.authenticate_user(form_data.password):
        if user.verified:
            jwt_token = JWTUserAccessToken(service, user)
            return jwt_token.encode_jwt()
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Account not verified")
        #return {"access_token": encode_jwt({"sub": user.username}, service), "token_type": "bearer"}
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Authorisation Error",
                            headers={"WWW-Authenticate": "Bearer"})


@router.post("/changepassword")
async def change_password(service: str,
                          form_data: Annotated[PasswordChangeForm, Depends()],
                          db: Session = Depends(get_db)):
    user = get_user_by_username(db, form_data.username, service)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Authorisation Error",
                            headers={"WWW-Authenticate": "Bearer"})
    if user.authenticate_user(form_data.old_password):
        user.password_hash = pwd_hasher.hash(form_data.new_password)
        db.commit()
        db.refresh(user)
        return {"msg": "Password changed"}
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Authorisation Error",
                            headers={"WWW-Authenticate": "Bearer"})


@router.post("/resetpassword")
async def request_password_reset(service: str,
                                 form_data: Annotated[PasswordResetRequestForm, Depends()],
                                 request: Request,
                                 background_tasks: BackgroundTasks,
                                 db: Session = Depends(get_db)):
    user = get_user_by_email(db, form_data.email, service)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED) #TODO do we want to do this as it alerts user that account doesn't exist?
    password_reset_email = PasswordResetEmail(user, service, str(request.url_for('verify_user')))
    background_tasks.add_task(password_reset_email.send_email)
    return {"msg": "Password reset requested"} # TODO as for above todo




