import json
from fastapi.testclient import TestClient
from models import Contact

from main import app

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
