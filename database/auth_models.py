from sqlalchemy import Boolean, Column, String, Integer
from sqlalchemy.orm import DeclarativeBase
from argon2 import PasswordHasher
from argon2 import exceptions as argonexceptions


class BaseUser(DeclarativeBase):
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    verified = Column(Boolean, default=False)
    password_locked = Column(Boolean, default=False)
    pwd_hasher = PasswordHasher()

    def authenticate_user(self, password):
        try:
            self.pwd_hasher.verify(self.password_hash, password)
        except argonexceptions.VerifyMismatchError:
            return False
        return True


class TourTrackerUser(BaseUser):
    __tablename__ = "tourtrackerusers"


class ArcadeUser(BaseUser):
    __tablename__ = "arcadeusers"
