"""Models for players (athletes) as they appear in API responses."""

from abc import ABC
from typing import Literal

from pydantic import BaseModel, Field

from pycricinfo.models.source.api.common import CCBaseModel, DisplayNameMixin, Link, Position, RefMixin


class Style(CCBaseModel):
    """Batting and Bowling styles for a Player."""

    description: str = Field(
        description="A description of the style, e.g. 'Right-hand bat', or 'Right-arm offbreak' etc"
    )
    short_description: str = Field(
        description="An abbreviated description of the style, e.g. 'Rhb'/'Lhb', or 'Rfm'/'Ob' etc"
    )
    type: Literal["batting", "bowling"] = Field(description="Whether this is a batting or bowling style")


class Headshot(RefMixin):
    """A link to a photo of a Player."""

    alt: str | None = Field(default=None, description="The alt text for the image. Contains the name of the Player.")


class ShortNameMixin(BaseModel):
    """Mixin property for a Player's short name."""

    short_name: str | None = Field(
        default=None, description="Short variant of the Player's name, usually just their last name"
    )


class FullNameMixin(BaseModel):
    """Mixin property for a Player's full name."""

    full_name: str | None = Field(default=None, description="Full name of the Player, including any middle names")


class FirstNameMixin(BaseModel):
    """Mixin property for a Player's first name."""

    first_name: str | None = Field(default=None, description="First name of the player")


class LastNameMixin(BaseModel):
    """Mixin property for a Player's last name."""

    last_name: str = Field(description="Last name of the Player")


class AthleteCommon(RefMixin, FullNameMixin, DisplayNameMixin, ABC):
    """Abstract base class for common fields across the different shapes of athlete in the API."""

    id: str | int = Field(description="The unique identifier for the athlete")


class AthleteWithNameAndShortName(AthleteCommon, ShortNameMixin):
    """An athlete with a name and short name, as included in ball-by-ball commentary."""

    name: str = Field(description="The full name of the athlete")


class AthleteWithFirstAndLastName(AthleteCommon, FirstNameMixin, LastNameMixin):
    """An athlete with a first and last name, as included in dismissals."""


class Athlete(AthleteWithFirstAndLastName, ShortNameMixin):
    """A Player, as included in match rosters and innings."""

    guid: str | None = Field(default=None, description="Unique identifier for the Player, in GUID format")
    uid: str = Field(
        description="Unique identifier for the Player, in a format custom to Cricinfo", examples=["s:200~a:931581"]
    )
    name: str = Field(description="Another variant of the name of the Player, usually just first and last names")
    style: list[Style] | None = None
    position: Position | None = None
    batting_name: str
    fielding_name: str
    headshot: Headshot | None = None
    links: list[Link]

    def __str__(self) -> str:
        """Describe the Player by name and Cricinfo ID."""
        return f"{self.name} ({self.uid})"
