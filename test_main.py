import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from db_utils import get_db
from database.auth_models import BaseUser, TourTrackerUser
from database.crud import create_user, get_user_by_username, get_user_by_email, get_user_by_public_id
from database.auth_schemas import UserCreate
from utils import pwd_hasher
from jwt_utilities import decode_jwt
from email_utils import VerificationEmail, PasswordResetEmail
from config import settings
from urllib.parse import urlparse, parse_qs

# Test database setup reference: https://dev.to/jbrocher/fastapi-testing-a-database-5ao5


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# settings.secret_key = 'test-jwt-secret'


@pytest.fixture(scope="function")
def test_jwts():
    yield {
        "expired_jwt": 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJNciBWZXJpZmllZCIsInNlcnZpY2UiOiJ0b3VydHJhY2tlci'
                       'IsImV4cCI6MTMxNjIzOTAyMn0.O_5dG4C0VpwkOnQlcOvHKwhAWSEWOlzCxkancejjYC0',
        "valid_jwt": 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJNciBWZXJpZmllZCIsInNlcnZpY2UiOiJ0b3VydHJhY2tlciIs'
                     'ImV4cCI6MzAxNjIzOTAyMn0.nVyR8iAlTwAKA9rTQGbfyn4Ildo88FuX-IPrJJP6sis',
        "modified_jwt": 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJNciBWZXJpZmllZCIsInNlcnZpY2UiOiJ0b3VydHJhY2tlc'
                        'iIsImV4cCI6MzAxNjIzOTAyMn0.nVyR8iAlTwAKA9rTQGbfyn4Ildo88FuX-IPrJJP6mod',
        "bad_algo_jwt": 'eyJhbGciOiJIUzM4NCIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJNciBWZXJpZmllZCIsInNlcnZpY2UiOiJ0b3VydHJhY2tlc'
                        'iIsImV4cCI6MzAxNjIzOTAyMn0.hd-sUftRDD34rTkUT5O82Y0NgH-yB1dLo6OksBGxK2rFZPX9KQSQYsPK3wgN6IL8'
    }


@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    TourTrackerUser.metadata.create_all(bind=engine)
    yield engine


@pytest.fixture(scope="function")
def db(db_engine):
    engine = db_engine
    connection = engine.connect()
    transaction = connection.begin()
    db = Session(bind=connection)
    yield db
    db.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db):
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="function")
def seed_db(db):
    verified_user = UserCreate(
        email="verified@test.com",
        username="Mr Verified",
        password_hash=pwd_hasher.hash("testpassword")
    )
    verified_user_object = create_user(db, verified_user, 'tourtracker')
    verified_user_object.verified = True
    db.commit()
    db.refresh(verified_user_object)

    non_verified_user = UserCreate(
        email="nonverified@test.com",
        username="Mrs NonVerified",
        password_hash=pwd_hasher.hash("testpassword")
    )
    non_verified_user_object = create_user(db, non_verified_user, 'tourtracker')

    password_locked_user = UserCreate(
        email="passwordlocked@test.com",
        username="Lady Locked",
        password_hash=pwd_hasher.hash("testpassword")
    )
    password_locked_user_object = create_user(db, password_locked_user, 'tourtracker')
    password_locked_user_object.verified = True
    password_locked_user_object.password_locked = True
    db.commit()
    db.refresh(password_locked_user_object)

    yield non_verified_user_object


def test_decode_jwt_expired(test_jwts):
    token = test_jwts['expired_jwt']
    with pytest.raises(HTTPException) as e:
        token = decode_jwt(token)
    assert e.value.status_code == 401
    assert e.value.detail == "Expired JWT Token"


def test_decode_jwt_bad_signature(test_jwts):
    token = test_jwts['modified_jwt']
    with pytest.raises(HTTPException) as e:
        token = decode_jwt(token)
    assert e.value.status_code == 400
    assert e.value.detail == "JWT Decode Error"


def test_decode_jwt_bad_algo(test_jwts):
    token = test_jwts['bad_algo_jwt']
    with pytest.raises(HTTPException) as e:
        token = decode_jwt(token)
    assert e.value.status_code == 400
    assert e.value.detail == "JWT Decode Error"


def test_decode_jwt(test_jwts):
    token = test_jwts['valid_jwt']
    payload = decode_jwt(token)
    assert payload['sub'] == 'Mr Verified'
    assert payload['service'] == 'tourtracker'


def test_get_user_by_username(db, seed_db):
    user = get_user_by_username(db, 'Mr Verified', 'tourtracker')
    assert user is not None
    assert user.email == 'verified@test.com'


def test_get_user_by_email(db, seed_db):
    user = get_user_by_email(db, 'verified@test.com', 'tourtracker')
    assert user is not None
    assert user.username == 'Mr Verified'


def test_get_user_by_public_id(db, seed_db):
    user = get_user_by_email(db, 'verified@test.com', 'tourtracker')
    public_id = user.public_id
    user_public_id = get_user_by_public_id(db, public_id, 'tourtracker')
    assert user_public_id is not None
    assert user_public_id.username == 'Mr Verified'


def test_create_user(client, db):
    user = UserCreate(
        email='test@test.com',
        username='CreateUser Test',
        password_hash='dummypasswordhash'
    )
    user_object = create_user(db, user=user, service='tourtracker')
    assert user_object.username == 'CreateUser Test'
    assert user_object.verified is False


def test_authenticate_user(db, seed_db):
    user = get_user_by_email(db, 'verified@test.com', 'tourtracker')
    assert user.authenticate_user("testpassword") is True


def test_signup(client, db):
    response = client.post(
        "/signup?service=tourtracker",
        data={"email": "test2@test.com",
              "username": "Joe Bloggs",
              "password": "testpassword123"}
    )
    assert response.status_code == 201
    user = get_user_by_username(db, 'Joe Bloggs', 'tourtracker')
    assert user is not None
    assert user.email == "test2@test.com"


def test_signup_email_already_exists(client, seed_db):
    response = client.post(
        "/signup/?service=tourtracker",
        data={"email": "verified@test.com",
              "username": "Joe Bloggs",
              "password": "testpassword123"}
    )
    assert response.status_code == 409
    assert response.json() == {"detail": "Email or username already registered."}


def test_signup_username_already_exists(client, seed_db):
    response = client.post(
        "/signup?service=tourtracker",
        data={"email": "test@test.com",
              "username": "Mr Verified",
              "password": "testpassword123"}
    )
    assert response.status_code == 409
    assert response.json() == {"detail": "Email or username already registered."}


def test_auth_invalid_username(client, seed_db):
    response = client.post(
        "/auth?service=tourtracker",
        data={"username": "invalid", "password": "password"}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Authorisation Error"}
    assert "WWW-Authenticate" in response.headers
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_auth_incorrect_password(client, seed_db):
    response = client.post(
        "/auth?service=tourtracker",
        data={"username": "Mr Verified", "password": "wrong password"}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Authorisation Error"}
    assert "WWW-Authenticate" in response.headers
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_auth_non_verified_user(client, seed_db):
    response = client.post(
        "/auth?service=tourtracker",
        data={"username": "Mrs NonVerified", "password": "testpassword"}
    )
    assert response.status_code == 403
    assert response.json() == {"detail": "Account not verified."}


def test_auth_password_locked(client, seed_db):
    response = client.post(
        "/auth?service=tourtracker",
        data={"username": "Lady Locked", "password": "testpassword"}
    )
    assert response.status_code == 403
    assert response.json() == {"detail": "Account not verified."}


def test_auth(client, seed_db):
    response = client.post(
        "/auth?service=tourtracker",
        data={"username": "Mr Verified", "password": "testpassword"}
    )
    assert response.status_code == 200
    assert response.cookies.get('__Secure-fgp') is not None
    for cookie in response.cookies.jar:
        assert cookie.secure is True
        assert cookie.get_nonstandard_attr('SameSite') == 'strict'
        assert cookie.has_nonstandard_attr('HttpOnly') is True


def test_change_password(client, db, seed_db):
    response = client.post(
        "/changepassword?service=tourtracker&username=Mr%20Verified",
        data={"old_password": "testpassword", "new_password": "newpassword"}
    )
    assert response.status_code == 200
    assert response.json() == {"detail": "Password changed"}
    user = get_user_by_email(db,"verified@test.com", "tourtracker")
    assert user.authenticate_user("newpassword") is True


def test_change_password_incorrect_old_password(client, db, seed_db):
    response = client.post(
        "/changepassword?service=tourtracker&username=Mr%20Verified",
        data={"old_password": "wrongpassword", "new_password": "newpassword"}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Authorisation Error"}
    assert "WWW-Authenticate" in response.headers
    assert response.headers["WWW-Authenticate"] == "Bearer"
    user = get_user_by_email(db,"verified@test.com", "tourtracker")
    assert user.authenticate_user("testpassword") is True


def test_verify_user(client, db, seed_db):
    user = get_user_by_email(db, 'nonverified@test.com', 'tourtracker')
    verification_email = VerificationEmail(user, 'tourtracker', 'http://127.0.0.1:8000', 'http://testserver')
    email_subject, token_url = verification_email.send_email()
    assert email_subject == "Please verify your email address"
    parsed_url = urlparse(token_url)
    query_strings = parse_qs(parsed_url[4])
    token = query_strings['token'][0]
    redirect_url = query_strings['redirect_url'][0]
    response = client.get(f"/verify?token={token}&redirect_url={redirect_url}", follow_redirects=False)
    assert user.verified is True
    assert response.is_redirect is True
    assert response.status_code == 307




def test_password_reset_request(client, db, seed_db):
    response = client.post('/resetpasswordrequest?service=tourtracker',
                          data={'email': 'verified@test.com'})
    assert response.status_code == 200
    assert response.json() == {"detail": "Password reset link sent if user exists."}


def test_password_reset_one_time_token(db, seed_db):
    user = get_user_by_email(db, "verified@test.com", "tourtracker")
    password_reset_email = PasswordResetEmail(user, 'tourtracker', 'http://127.0.0.1', 'https://redirect.to')
    secret_key = f"{user.password_hash}_{user.created_at}"
    parsed_url = urlparse(password_reset_email.token_url)
    query_strings = parse_qs(parsed_url[4])
    token = query_strings['token'][0]
    payload = decode_jwt(token, secret_key=secret_key)
    assert payload['sub'] == user.public_id


def test_password_reset(client, db, seed_db):
    user = get_user_by_email(db, "verified@test.com", "tourtracker")
    password_reset_email = PasswordResetEmail(user, 'tourtracker')
    password_reset_url = password_reset_email.token_url
    print(password_reset_url)
    response = client.post(password_reset_url,
                           data={'new_password': 'newpassword'})
    print(password_reset_url)
    assert response.status_code == 200
    assert user.authenticate_user("newpassword") is True


def test_generate_user_fingerprint():
    user = BaseUser(email='test@test.com', username='test', password_hash='dummypasswordhash')
    fingerprint, fingerprint_hash = user.generate_user_fingerprint()
    assert user.pwd_hasher.verify(fingerprint_hash, fingerprint) is True


