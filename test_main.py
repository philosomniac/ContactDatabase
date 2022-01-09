import json
from fastapi.testclient import TestClient
import models
import db_models
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from deps import get_db

from main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


def initialize_test_db():
    try:
        db = TestingSessionLocal()
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

        test_user = db_models.User(id=1, username="johndoe",
                                   hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW")
        db.add(test_user)
        db.commit()
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

initialize_test_db()

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}


def test_read_contact1():
    response = client.get("/contacts/1")
    assert response.status_code == 200
    json = response.json()
    assert json["first_name"] is not None
    assert json["last_name"] is not None
    assert json["address"] is not None
    assert json["email"] is not None
    assert json["city"] is not None
    assert json["state"] is not None
    assert json["zip_code"] is not None


def test_add_contact():
    testcontact = {
        'first_name': 'John',
        'last_name': 'Smith',
        'address': '456 1st st',
        'email': 'jsmith@email.com',
        'city': 'Green Bay',
        'state': 'WI',
        'zip_code': '54303'
    }
    response = client.post("/contacts/", json=testcontact)
    assert response.status_code == 200
    assert all(key in response.json().keys() for key in testcontact.keys())
