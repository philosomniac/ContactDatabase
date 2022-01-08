from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class Contact(Base):
    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    address = Column(String)
    city = Column(String)
    state = Column(String)
    zip_code = Column(String)

    phones = relationship("Phone", back_populates="contact")


class Phone(Base):
    __tablename__ = 'phones'

    id = Column(Integer, primary_key=True, index=True)
    phone_type = Column(String)
    phone_number = Column(String)
    contact_id = Column(Integer, ForeignKey("contacts.id"))

    contact = relationship("Contact", back_populates="phones")
