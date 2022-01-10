from sqlalchemy.orm import Session

import models
import db_models
import security


def get_contact(db: Session, contact_id: int) -> db_models.Contact:
    return db.get(db_models.Contact, contact_id)


def create_contact(db: Session, contact: models.ContactCreate) -> db_models.Contact:
    # hacky workaround to create phones+contacts
    phones_to_add: list[models.PhoneBase] = []
    for phone in contact.phones:
        phones_to_add.append(phone)
    contact.phones = []
    db_contact = db_models.Contact(**contact.dict())
    for phone in phones_to_add:
        db_contact.phones.append(db_models.Phone(**phone.dict()))

    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


def update_contact(db: Session, contact_id: int, contact: models.ContactBase) -> db_models.Contact:
    db_contact = db.get(db_models.Contact, contact_id)
    db_contact.__dict__.update(contact.dict())
    db.commit()
    return db_contact


def delete_contact(db: Session, contact_id: int):
    db_contact = db.get(db_models.Contact, contact_id)
    db.delete(db_contact)
    db.commit()
    return db_contact


def create_phone(db: Session, contact_id: int, phone: models.PhoneCreate) -> db_models.Phone:
    db_phone = db_models.Phone(**phone.dict())
    db_phone.contact_id = contact_id
    db.add(db_phone)
    db.commit()
    db.refresh(db_phone)
    return db_phone


def get_phone(db: Session, phone_id: int) -> db_models.Phone:
    return db.get(db_models.Phone, phone_id)


def update_phone(db: Session, phone_id: int, phone: models.PhoneBase) -> db_models.Phone:
    db_phone = db.get(db_models.Phone, phone_id)
    db_phone.__dict__.update(phone.dict())
    db.commit()
    return db_phone


def delete_phone(db: Session, phone_id: int) -> db_models.Phone:
    db_phone = db.get(db_models.Phone, phone_id)
    db.delete(db_phone)
    db.commit()
    return db_phone


def get_user(db: Session, username: str) -> db_models.User:
    return db.query(db_models.User).filter(db_models.User.username == username).first()


def authenticate_user(username: str, password: str, db: Session):
    user = get_user(db, username)
    if not user:
        return False
    if not security.verify_password(password, user.hashed_password):
        return False
    return user
