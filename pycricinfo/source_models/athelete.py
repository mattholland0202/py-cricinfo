from abc import ABC
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl

from pycricinfo.source_models.common import CCBaseModel, DisplayNameMixin, IDMixin, Link, NameMixin, RefMixin


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


class AthleteCommon(RefMixin, IDMixin, FullNameMixin, DisplayNameMixin, ABC): ...


class AthleteWithNameAndShortName(AthleteCommon, NameMixin, ShortNameMixin): ...


class AthleteWithFirstAndLastName(AthleteCommon, FirstNameMixin, LastNameMixin): ...


class Athlete(AthleteWithFirstAndLastName):
    guid: Optional[str] = None
    uid: str
    name: str
    style: list[Style]
    batting_name: str
    fielding_name: str
    headshot: Optional[Headshot] = None
    links: list[Link]

    def __str__(self) -> str:
        return f"{self.name} ({self.uid})"
