from abc import ABC
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl

from pycricinfo.source_models.api.common import CCBaseModel, DisplayNameMixin, Link, RefMixin


class Style(CCBaseModel):
    description: str
    short_description: str
    type: str


class Headshot(BaseModel):
    href: HttpUrl
    rel: list[str]


class ShortNameMixin(BaseModel):
    short_name: str


class FullNameMixin(BaseModel):
    full_name: Optional[str] = Field(default=None)


class FirstNameMixin(BaseModel):
    first_name: Optional[str] = Field(default=None)


class LastNameMixin(BaseModel):
    last_name: str


class AthleteCommon(RefMixin, FullNameMixin, DisplayNameMixin, ABC):
    id: str|int = Field(description="The unique identifier for the athlete")


class AthleteWithNameAndShortName(AthleteCommon, ShortNameMixin):
    name: str = Field(description="The full name of the athlete")


class AthleteWithFirstAndLastName(AthleteCommon, FirstNameMixin, LastNameMixin): ...


class Athlete(AthleteWithFirstAndLastName):
    guid: Optional[str] = None
    uid: str
    name: str
    style: Optional[list[Style]] = None
    batting_name: str
    fielding_name: str
    headshot: Optional[Headshot] = None
    links: list[Link]

    def __str__(self) -> str:
        return f"{self.name} ({self.uid})"
