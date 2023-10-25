from typing import Annotated
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from routes import router
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings

allowed_origins = list(settings.ALLOWED_ORIGINS)

# Database setup
app = FastAPI(debug=settings.DEBUG)
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=['GET', 'POST'],
    allow_credentials=True
)
app.include_router(router)
