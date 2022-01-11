from datetime import timedelta

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import db_models
import models
import security
from database import Base
from deps import get_db
from main import app
from testing_data import initial_contacts, initial_user

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


def initialize_test_db(test_user, initial_contacts):
    try:
        db = TestingSessionLocal()

        db.add(db_models.User(**test_user))
        for contact in initial_contacts:
            for phone in contact['phones']:
                db.add(db_models.Phone(**phone))
            del contact['phones']
            db.add(db_models.Contact(**contact))
        db.commit()
    finally:
        db.close()


initialize_test_db(initial_user, initial_contacts)
app.dependency_overrides[get_db] = override_get_db


client = TestClient(app)


@pytest.fixture
def test_contact():
    return {
        'first_name': 'John',
        'last_name': 'Smith',
        'address': '456 1st st',
        'email': 'jsmith@email.com',
        'city': 'Green Bay',
        'state': 'WI',
        'zip_code': '54303',
        'phones': [
            {'phone_type': 'mobile',
             'phone_number': '5551234567',
             },
            {'phone_type': 'home',
             'phone_number': '5551234568',
             }
        ]
    }


@pytest.fixture
def test_phone():
    return {
        'phone_type': 'mobile',
        'phone_number': '5555555555'
    }


@pytest.fixture
def valid_access_token():
    return security.create_access_token(
        data={"sub": initial_user['username']}, expires_delta=timedelta(minutes=60))


@pytest.fixture
def valid_access_header(valid_access_token):
    return {'Authorization': 'Bearer ' + valid_access_token}


def test_read_main():
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"msg": "Hello World"}


def test_login_for_access_token_success():
    response = client.post(
        "/token", data={'username': initial_user['username'], 'password': 'secret'})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['access_token'] is not None


def test_login_for_access_token_failure():
    response = client.post(
        "/token", data={'username': 'bad_user_name', 'password': 'bad_pass'})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_read_contact1(valid_access_header):
    response = client.get("/contacts/1", headers=valid_access_header)
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json["first_name"] is not None
    assert json["last_name"] is not None
    assert json["address"] is not None
    assert json["email"] is not None
    assert json["city"] is not None
    assert json["state"] is not None
    assert json["zip_code"] is not None


def test_add_contact_with_auth_should_200(test_contact, valid_access_header):
    response = client.post("/contacts", json=test_contact,
                           headers=valid_access_header)
    assert response.status_code == status.HTTP_200_OK
    assert all(key in response.json().keys() for key in test_contact.keys())


def test_crud_without_auth_should_401(test_contact, test_phone):

    headers = {'Authorization': 'Bearer ' + "not_an_access_token"}

    response = client.post("/contacts", json=test_contact, headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response = client.get("/contacts/1", headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response = client.put("/contacts/2", json=test_contact, headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response = client.delete("/contacts/2", headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response = client.get("/contacts/1/phones/1", headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response = client.post("/contacts/1/phones",
                           json=test_phone, headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response = client.put("/contacts/1/phones/2",
                          json=test_phone, headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response = client.delete("/contacts/1/phones/2", headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_invalid_email_should_422(test_contact, valid_access_header):
    test_contact['email'] = "not_an_email"
    response = client.post("/contacts", json=test_contact,
                           headers=valid_access_header)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_invalid_zip_should_422(test_contact, valid_access_header):
    # too short
    test_contact['zip_code'] = "42"
    response = client.post("/contacts", json=test_contact,
                           headers=valid_access_header)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # too long
    test_contact['zip_code'] = "42860484"
    response = client.post("/contacts", json=test_contact,
                           headers=valid_access_header)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    #not numeric
    test_contact['zip_code'] = "bad29"
    response = client.post("/contacts", json=test_contact,
                           headers=valid_access_header)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_invalid_phone_should_422(test_phone, valid_access_header):
    # too short
    test_phone['phone_number'] = "42"
    response = client.post("/contacts/1/phones",
                           json=test_phone, headers=valid_access_header)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # too long
    test_phone['phone_number'] = "123456789012"
    response = client.post("/contacts/1/phones",
                           json=test_phone, headers=valid_access_header)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # too long after pre-process
    test_phone['phone_number'] = "1 (234) 567-89012"
    response = client.post("/contacts/1/phones",
                           json=test_phone, headers=valid_access_header)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_valid_phone_after_preprocessing(test_phone, valid_access_header):
    # valid
    test_phone['phone_number'] = "12345678901"
    response = client.post("/contacts/1/phones",
                           json=test_phone, headers=valid_access_header)
    assert response.status_code == status.HTTP_200_OK

    # valid after pre-process
    test_phone['phone_number'] = "1 (234) 567-8901"
    response = client.post("/contacts/1/phones",
                           json=test_phone, headers=valid_access_header)
    assert response.status_code == status.HTTP_200_OK
