from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import db_models

SQLALCHEMY_DATABASE_URL = 'sqlite:///./contacts_app.db'

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={
                       "check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def db_initialize():
    Base.metadata.create_all(bind=engine)

    # from testing_data import initial_user, initial_contacts
    # load_test_data(SessionLocal(), initial_user, initial_contacts)


def load_test_data(db: Session, initial_user, initial_contacts):
    try:
        db.add(db_models.User(**initial_user))
        for contact in initial_contacts:
            for phone in contact['phones']:
                db.add(db_models.Phone(**phone))
            del contact['phones']
            db.add(db_models.Contact(**contact))
        db.commit()
    finally:
        db.close()
