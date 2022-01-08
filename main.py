from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import crud
import models
import db_models

db_models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def read_root():
    return {"msg": "Hello World"}


@app.get("/contacts/{id}", response_model=models.Contact)
def read_contact(id: int, db: Session = Depends(get_db)):
    db_contact = crud.get_contact(db, contact_id=id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Could not find contact")
    return db_contact


@app.post("/contacts/", response_model=models.Contact)
def create_contact(contact: models.ContactBase, db: Session = Depends(get_db)):
    return crud.create_contact(db=db, contact=contact)
