from abc import ABC
from typing import Literal, Optional

from pydantic import BaseModel, Field

from pycricinfo.models.source.api.common import CCBaseModel, DisplayNameMixin, FlagMixin, Link, Position, RefMixin


class Style(CCBaseModel):
    """
    Batting and Bowling styles for a Player.
    """

    description: str = Field(
        description="A description of the style, e.g. 'Right-hand bat', or 'Right-arm offbreak' etc"
    )
    short_description: str = Field(
        description="An abbreviated description of the style, e.g. 'Rhb'/'Lhb', or 'Rfm'/'Ob' etc"
    )
    type: Literal["batting", "bowling"] = Field(description="Whether this is a batting or bowling style")


class Headshot(RefMixin):
    alt: Optional[str] = Field(default=None, description="The alt text for the image. Contains the name of the Player.")


class ShortNameMixin(BaseModel):
    short_name: Optional[str] = Field(
        default=None, description="Short variant of the Player's name, usually just their last name"
    )


class FullNameMixin(BaseModel):
    full_name: Optional[str] = Field(default=None, description="Full name of the Player, including any middle names")


class FirstNameMixin(BaseModel):
    first_name: Optional[str] = Field(default=None, description="First name of the player")


class LastNameMixin(BaseModel):
    last_name: str = Field(description="Last name of the Player")


class AthleteCommon(RefMixin, FullNameMixin, DisplayNameMixin, ABC):
    id: str | int = Field(description="The unique identifier for the athlete")


class AthleteWithNameAndShortName(AthleteCommon, ShortNameMixin):
    name: str = Field(description="The full name of the athlete")


class AthleteWithFirstAndLastName(AthleteCommon, FirstNameMixin, LastNameMixin): ...


class Athlete(AthleteWithFirstAndLastName, ShortNameMixin):
    guid: Optional[str] = Field(default=None, description="Unique identifier for the Player, in GUID format")
    uid: str = Field(
        description="Unique identifier for the Player, in a format custom to Cricinfo", examples=["s:200~a:931581"]
    )
    name: str = Field(description="Another variant of the name of the Player, usually just first and last names")
    style: Optional[list[Style]] = None
    position: Optional[Position] = None
    batting_name: str
    fielding_name: str
    headshot: Optional[Headshot] = None
    links: list[Link]
    debuts: Optional[list[RefMixin]] = None
    major_teams: Optional[list[RefMixin]] = None
    flag: FlagMixin

    def __str__(self) -> str:
        return f"{self.name} ({self.uid})"
