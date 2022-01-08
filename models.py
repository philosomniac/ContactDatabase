
from pydantic import BaseModel


class User(BaseModel):
    username: str


class UserInDB(User):
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class PhoneBase(BaseModel):
    phone_type: str
    phone_number: str


class Phone(PhoneBase):
    id: int
    contact_id: int

    class Config:
        orm_mode = True


class ContactBase(BaseModel):
    first_name: str
    last_name: str
    address: str
    city: str
    state: str
    zip_code: str
    email: str
    phones: list[Phone] = []


class Contact(ContactBase):
    id: int

    class Config:
        orm_mode = True
