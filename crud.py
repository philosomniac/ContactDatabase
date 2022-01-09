from sqlalchemy.orm import Session

import models
import db_models
import security


def get_contact(db: Session, contact_id: int) -> db_models.Contact:
    return db.get(db_models.Contact, contact_id)


def create_contact(db: Session, contact: models.ContactBase) -> db_models.Contact:
    db_contact = db_models.Contact(**contact.dict())
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


def get_user(db: Session, username: str) -> db_models.User:
    return db.query(db_models.User).filter(db_models.User.username == username).first()


def authenticate_user(username: str, password: str, db: Session):
    user = get_user(db, username)
    if not user:
        return False
    if not security.verify_password(password, user.hashed_password):
        return False
    return user
