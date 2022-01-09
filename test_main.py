import json
from fastapi.testclient import TestClient
import models
import db_models
import security
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from deps import get_db
from datetime import timedelta
import pytest

from main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


def initialize_test_db(test_user, test_contact):
    try:
        db = TestingSessionLocal()

        db.add(db_models.User(**test_user))
        db.add(db_models.Contact(**test_contact))
        db.commit()
    finally:
        db.close()


test_user_dict = {'id': 1,
                  'username': "johndoe",
                  'hashed_password': "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"}

test_contact_dict = {
    'id': 1,
    'first_name': 'John',
    'last_name': 'Smith',
    'address': '456 1st st',
    'email': 'jsmith@email.com',
    'city': 'Green Bay',
    'state': 'WI',
    'zip_code': '54303'}
initialize_test_db(test_user_dict, test_contact_dict)
app.dependency_overrides[get_db] = override_get_db


client = TestClient(app)


@pytest.fixture
def valid_access_token():
    return security.create_access_token(
        data={"sub": test_user_dict['username']}, expires_delta=timedelta(minutes=60))


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}


def test_login_for_access_token_success():
    response = client.post(
        "/token", data={'username': test_user_dict['username'], 'password': 'secret'})
    assert response.status_code == 200
    assert response.json()['access_token'] is not None


def test_login_for_access_token_failure():
    response = client.post(
        "/token", data={'username': 'bad_user_name', 'password': 'bad_pass'})
    assert response.status_code == 401


def test_read_contact1(valid_access_token):
    response = client.get(
        "/contacts/1", headers={'Authorization': 'Bearer ' + valid_access_token})
    assert response.status_code == 200
    json = response.json()
    assert json["first_name"] is not None
    assert json["last_name"] is not None
    assert json["address"] is not None
    assert json["email"] is not None
    assert json["city"] is not None
    assert json["state"] is not None
    assert json["zip_code"] is not None


def test_add_contact(valid_access_token):
    testcontact = {
        'first_name': 'John',
        'last_name': 'Smith',
        'address': '456 1st st',
        'email': 'jsmith@email.com',
        'city': 'Green Bay',
        'state': 'WI',
        'zip_code': '54303'
    }
    response = client.post("/contacts", json=testcontact,
                           headers={'Authorization': 'Bearer ' + valid_access_token})
    assert response.status_code == 200
    assert all(key in response.json().keys() for key in testcontact.keys())
