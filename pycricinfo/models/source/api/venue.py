"""Models for venues."""

from pycricinfo.models.source.api.common import CCBaseModel, Link, RefMixin


class Address(CCBaseModel):
    """The address of a venue."""

    city: str
    state: str | None = None
    zip_code: str | None = None
    country: str
    summary: str


class Venue(CCBaseModel):
    """A ground where matches are played."""

    id: str
    full_name: str
    short_name: str
    address: Address
    capacity: int
    grass: bool
    images: list[RefMixin]
    links: list[Link]
