from datetime import datetime, timedelta

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import crud
import deps
import models
import security
import settings
from database import db_initialize

db_initialize()

app = FastAPI()


@app.get("/")
def read_root():
    return {"msg": "Hello World"}


@app.post("/token", response_model=models.Token)
async def login_for_access_token(db: Session = Depends(deps.get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = crud.authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=models.User)
async def read_users_me(current_user: models.User = Depends(deps.get_current_user)):
    return current_user


@app.post("/contacts", response_model=models.Contact, dependencies=[Depends(deps.get_current_user)])
def create_contact(contact: models.ContactCreate, db: Session = Depends(deps.get_db)):
    return crud.create_contact(db=db, contact=contact)


@app.get("/contacts", response_model=list[models.Contact], dependencies=[Depends(deps.get_current_user)])
def read_contacts(skip: int = 0, limit: int = 10, db: Session = Depends(deps.get_db)):
    db_contacts = crud.get_contacts(db=db, skip=skip, limit=limit)
    if len(db_contacts) < 1:
        raise HTTPException(status_code=404, detail="No contacts present")
    return db_contacts


@app.get("/contacts/{contact_id}", response_model=models.Contact, dependencies=[Depends(deps.get_current_user)])
def read_contact(contact_id: int, db: Session = Depends(deps.get_db)):
    db_contact = crud.get_contact(db, contact_id=contact_id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Could not find contact")
    return db_contact


@app.put("/contacts/{contact_id}", response_model=models.Contact, dependencies=[Depends(deps.get_current_user)])
def update_contact(contact_id: int, contact: models.ContactBase, db: Session = Depends(deps.get_db)):
    db_contact = crud.get_contact(db, contact_id=contact_id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Could not find contact")
    db_contact = crud.update_contact(
        db, contact_id=contact_id, contact=contact)
    return db_contact


@app.delete("/contacts/{contact_id}", response_model=models.Contact, dependencies=[Depends(deps.get_current_user)])
def delete_contact(contact_id: int, db: Session = Depends(deps.get_db)):
    db_contact = crud.get_contact(db, contact_id=contact_id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Could not find contact")
    db_contact = crud.delete_contact(db, contact_id=contact_id)
    return db_contact


@app.post("/contacts/{contact_id}/phones", response_model=models.Phone, dependencies=[Depends(deps.get_current_user)])
def create_phone(contact_id: int, phone: models.PhoneBase, db: Session = Depends(deps.get_db)):
    db_contact = crud.get_contact(db, contact_id=contact_id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Could not find contact")
    db_phone = crud.create_phone(db, contact_id=contact_id, phone=phone)
    return db_phone


@app.put("/contacts/{contact_id}/phones/{phone_id}", response_model=models.Phone, dependencies=[Depends(deps.get_current_user)])
def update_phone(contact_id: int, phone_id: int, phone: models.PhoneBase, db: Session = Depends(deps.get_db)):
    db_phone = crud.get_phone(db, phone_id=phone_id)
    if db_phone is None:
        raise HTTPException(status_code=404, detail="Could not find phone")
    db_phone = crud.update_phone(db, phone_id=phone_id, phone=phone)
    return db_phone


@app.get("/contacts/{contact_id}/phones/{phone_id}", response_model=models.Phone, dependencies=[Depends(deps.get_current_user)])
def get_phone(contact_id: int, phone_id: int, db: Session = Depends(deps.get_db)):
    db_phone = crud.get_phone(db, phone_id=phone_id)
    if db_phone is None:
        raise HTTPException(status_code=404, detail="Could not find phone")
    return db_phone


@app.delete("/contacts/{contact_id}/phones/{phone_id}", response_model=models.Phone, dependencies=[Depends(deps.get_current_user)])
def delete_phone(contact_id: int, phone_id: int, db: Session = Depends(deps.get_db)):
    db_phone = crud.get_phone(db, phone_id=phone_id)
    if db_phone is None:
        raise HTTPException(status_code=404, detail="Could not find phone")
    crud.delete_phone(db, phone_id=phone_id)
    return db_phone
