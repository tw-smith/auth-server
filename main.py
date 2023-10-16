from typing import Annotated
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from routes import router
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

allowed_origins = [
    'https://tourtracker.tw-smith.me',
    'https://arcade.tw-smith.me',
    'http://localhost:4200',
    'http://127.0.0.1:8000',
]

# Database setup
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=['GET', 'POST'],
    allow_credentials=True
)
app.include_router(router)
