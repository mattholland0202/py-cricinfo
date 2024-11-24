from pydantic import BaseModel
from typing import Optional
from cricinfo.source_models.common import Ref, Link

class Address(BaseModel):
    city: str
    state: Optional[str] = None
    zipCode: Optional[str] = None
    country: str
    summary: str

class Venue(BaseModel):
    id: str
    fullName: str
    shortName: str
    address: Address
    capacity: int
    grass: bool
    images: list[Ref]
    links: list[Link]