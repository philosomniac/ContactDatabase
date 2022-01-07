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
    assert json["first_name"] == "Clark"
    assert json["last_name"] == "Kent"
    assert json["address"] == "123 main st"
    assert json["email"] == "ckent@email.com"
    assert json["city"] == "Metropolis"
    assert json["state"] == "NY"
    assert json["zip_code"] == "54321"


def test_add_contact():
    testcontact = {
        'id': '3',
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
