from typing import Optional

from pycricinfo.source_models.api.common import CCBaseModel, Link, RefMixin


class Address(CCBaseModel):
    city: str
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: str
    summary: str


class Venue(CCBaseModel):
    id: str
    full_name: str
    short_name: str
    address: Address
    capacity: int
    grass: bool
    images: list[RefMixin]
    links: list[Link]
