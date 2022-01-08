from sqlalchemy.orm import Session

import models
import db_models


def get_contact(db: Session, contact_id: int) -> db_models.Contact:
    return db.query(db_models.Contact).filter(db_models.Contact.id == contact_id).first()


def create_contact(db: Session, contact: models.ContactBase) -> db_models.Contact:
    db_contact = db_models.Contact(**contact.dict())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


def get_user(db: Session, username: str) -> db_models.User:
    return db.query(db_models.User).filter(db_models.User.username == username).first()
