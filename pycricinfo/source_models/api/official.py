from pydantic import BaseModel, HttpUrl

from pycricinfo.source_models.api.common import CCBaseModel, Link, Position


class Flag(BaseModel):
    alt: str
    height: int
    href: HttpUrl
    rel: list[str]
    width: int


class Official(CCBaseModel):
    display_name: str
    flag: Flag
    links: Link
    order: int
    position: Position
