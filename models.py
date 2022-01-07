
from pydantic import BaseModel


class Contact(BaseModel):
    id: int
    first_name: str
    last_name: str
    address: str
    city: str
    state: str
    zip_code: str
    email: str
