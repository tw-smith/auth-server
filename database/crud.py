from sqlalchemy.orm import Session
from . import auth_models, auth_schemas

# TODO: try and collate all these match case statements for DRY and improved maintainability

def get_user_by_id(db: Session, user_id: int, service):
    match service:
        case "tourtracker":
            return db.query(auth_models.TourTrackerUser).filter(auth_models.TourTrackerUser.id == user_id).first()
        case "arcade":
            return db.query(auth_models.ArcadeUser).filter(auth_models.ArcadeUser.id == user_id).first()


def get_user_by_email(db: Session, email: str, service):
    match service:
        case "tourtracker":
            return db.query(auth_models.TourTrackerUser).filter(auth_models.TourTrackerUser.email == email).first()
        case "arcade":
            return db.query(auth_models.ArcadeUser).filter(auth_models.ArcadeUser.email == email).first()


def get_user_by_username(db: Session, username: str, service):
    match service:
        case "tourtracker":
            return db.query(auth_models.TourTrackerUser).filter(auth_models.TourTrackerUser.username == username).first()
        case "arcade":
            return db.query(auth_models.ArcadeUser).filter(auth_models.ArcadeUser.username == username).first()


def create_user(db: Session, user: auth_schemas.UserCreate, service):
    match service:
        case "tourtracker":
            db_user = auth_models.TourTrackerUser(email=user.email, username=user.username, password_hash=user.password_hash)
        case "arcade":
            db_user = auth_models.ArcadeUser(email=user.email, username=user.username, password_hash=user.password_hash)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user



