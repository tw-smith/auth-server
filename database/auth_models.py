from sqlalchemy import Boolean, Column, String, Integer
from sqlalchemy.orm import DeclarativeBase
from argon2 import PasswordHasher
from argon2 import exceptions as argonexceptions
import secrets


class BaseUser(DeclarativeBase):
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    public_id = Column(String, unique=True, index=True)
    password_hash = Column(String)
    verified = Column(Boolean, default=False)
    password_locked = Column(Boolean, default=False)
    created_at = Column(Integer)
    pwd_hasher = PasswordHasher()

    def authenticate_user(self, password):
        try:
            self.pwd_hasher.verify(self.password_hash, password)
        except argonexceptions.VerifyMismatchError:
            return False
        return True

    def generate_user_fingerprint(self):
        fingerprint = secrets.token_urlsafe(32)
        fingerprint_hash = self.pwd_hasher.hash(fingerprint)
        return fingerprint, fingerprint_hash


class TourTrackerUser(BaseUser):
    __tablename__ = "tourtrackerusers"


class ArcadeUser(BaseUser):
    __tablename__ = "arcadeusers"
