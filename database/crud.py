import uuid

from sqlalchemy.orm import Session
from . import auth_models, auth_schemas
import time


# TODO: try and collate all these match case statements for DRY and improved maintainability


def get_user_by_public_id(db: Session, public_id: str, service) -> auth_models.BaseUser:
    match service:
        case "tourtracker":
            return db.query(auth_models.TourTrackerUser).filter(auth_models.TourTrackerUser.public_id == public_id).first()
        case "arcade":
            return db.query(auth_models.ArcadeUser).filter(auth_models.ArcadeUser.public_id == public_id).first()


def get_user_by_email(db: Session, email: str, service) -> auth_models.BaseUser:
    match service:
        case "tourtracker":
            return db.query(auth_models.TourTrackerUser).filter(auth_models.TourTrackerUser.email == email).first()
        case "arcade":
            return db.query(auth_models.ArcadeUser).filter(auth_models.ArcadeUser.email == email).first()


def get_user_by_username(db: Session, username: str, service) -> auth_models.BaseUser:
    match service:
        case "tourtracker":
            return db.query(auth_models.TourTrackerUser).filter(auth_models.TourTrackerUser.username == username).first()
        case "arcade":
            return db.query(auth_models.ArcadeUser).filter(auth_models.ArcadeUser.username == username).first()


def create_user(db: Session, user: auth_schemas.UserCreate, service) -> auth_models.BaseUser:
    match service:
        case "tourtracker":
            db_user = auth_models.TourTrackerUser(email=user.email, username=user.username, password_hash=user.password_hash)
        case "arcade":
            db_user = auth_models.ArcadeUser(email=user.email, username=user.username, password_hash=user.password_hash)
    db_user.created_at = int(time.time())
    db_user.public_id = str(uuid.uuid4())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user



