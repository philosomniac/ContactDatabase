
from pydantic import BaseModel, Field, validator


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
    phone_type: str = Field(example="mobile")
    phone_number: str = Field(
        min_length=10, max_length=11, example="1234567890")

    @validator('phone_number', pre=True)
    def validate_phone(cls, v):
        filtered = filter(str.isdigit, v)
        numeric = "".join(filtered)
        return numeric

    class Config:
        orm_mode = True


class PhoneCreate(PhoneBase):
    contact_id: int


class Phone(PhoneCreate):
    id: int

    class Config:
        orm_mode = True


class ContactBase(BaseModel):
    first_name: str = Field(..., example="Clark")
    last_name: str = Field(..., example="Kent")
    address: str = Field(..., example="123 Main St.")
    city: str = Field(..., example="Metropolis")
    state: str = Field(
        description="Two-character state abbreviation", example="NY", min_length=2, max_length=2, regex="^\w{2}$")
    zip_code: str = Field(description="5-digit zip code", example="12345",
                          min_length=5, max_length=5, regex="^\d{5}$")
    email: str = Field(description="Email address",
                       example="name@domain.com", regex=".+@.+")
    pass


class ContactCreate(ContactBase):
    phones: list[PhoneBase] = Field([], example=[{'phone_type': 'mobile',
                                                  'phone_number': '5551234567',
                                                  },
                                                 {'phone_type': 'home',
                                                  'phone_number': '5551234568',
                                                  }])


class Contact(ContactCreate):
    id: int

    phones: list[Phone] = Field([], example=[{'phone_type': 'mobile',
                                              'phone_number': '5551234567',
                                              'contact_id': 1,
                                              'id': 1
                                              },
                                             {'phone_type': 'home',
                                              'phone_number': '5551234568',
                                              'contact_id': 1,
                                              'id': 2
                                              }])

    class Config:
        orm_mode = True
