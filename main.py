from fastapi import FastAPI
from mock_db import db
from models import Contact

app = FastAPI()


@app.get("/")
def read_root():
    return {"msg": "Hello World"}


@app.get("/contacts/{id}")
def read_contact(id: int):
    # get contact
    contact: Contact = [c for c in db if c.id == id][0]
    return contact


@app.post("/contacts/")
def add_contact(contact: Contact):
    db.append(contact)
    return contact
