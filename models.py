
from pydantic import BaseModel, Field


class User(BaseModel):
    username: str

    class Config:
        orm_mode = True


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

    class Config:
        orm_mode = True


class PhoneCreate(PhoneBase):
    contact_id: int


class Phone(PhoneCreate):
    id: int

    class Config:
        orm_mode = True


class ContactBase(BaseModel):
    first_name: str
    last_name: str
    address: str
    city: str
    state: str = Field(
        description="Two-character state abbreviation", min_length=2, max_length=2)
    zip_code: str = Field(description="5-digit zip code",
                          min_length=5, max_length=5)
    email: str = Field(description="Email address", regex=".+@.+")
    pass


class ContactCreate(ContactBase):
    phones: list[PhoneBase] = []


class Contact(ContactCreate):
    id: int

    phones: list[Phone] = []

    class Config:
        orm_mode = True
