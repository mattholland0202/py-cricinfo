from typing import Optional

from pydantic import BaseModel, HttpUrl

from cricinfo.source_models.common import Link, CCBaseModel, Ref


class Style(CCBaseModel):
    description: str
    short_description: str
    type: str

class Headshot(BaseModel):
    href: HttpUrl
    rel: list[str]

class AthleteLite(Ref):
    id: int
    display_name: str
    first_name: Optional[str] = None
    last_name: str
    full_name: str

class Athlete(AthleteLite):
    guid: Optional[str] = None
    uid: str
    name: str
    style: list[Style]
    batting_name: str
    fielding_name: str
    headshot: Optional[Headshot] = None
    links: list[Link]