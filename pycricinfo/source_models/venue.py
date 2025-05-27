from typing import Optional

from pydantic import BaseModel

from pycricinfo.source_models.common import Link, RefMixin


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
    images: list[RefMixin]
    links: list[Link]
