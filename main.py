from typing import Annotated
from fastapi import FastAPI, Depends
from routes import router
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# Database setup
app = FastAPI()
app.include_router(router)