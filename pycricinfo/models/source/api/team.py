"""Models for Teams, and the wickets and overs in a Team's innings."""

from abc import ABC

from pydantic import AliasChoices, Field

from pycricinfo.models.source.api.common import CCBaseModel, Event, RefMixin


class TeamCommon(CCBaseModel, ABC):
    """Abstract base class for common fields across the different shapes of Team in the API."""

    id: str
    abbreviation: str
    display_name: str


class TeamWithName(TeamCommon):
    """A Team with its full name."""

    name: str = Field(description="The full name of the Team")


class TeamWithColorAndLogos(TeamCommon):
    """A Team with its colour and logos, as included in match data."""

    color: str = Field(description="The hex colour for the Team", examples=["#790d1a"])
    logos: list[RefMixin]


class TeamFull(TeamWithName):
    """A Team's full details, as returned by the teams API."""

    # TODO: Format "classes" field onto what match type they represent
    color: str
    nickname: str
    short_display_name: str
    is_national: bool
    is_active: bool
    classes: list[int] = Field(description="The classes of match that this Team plays in")
    current_match: Event | None = Field(default=None, validation_alias=AliasChoices("event"))
    current_players_link: RefMixin | None = Field(default=None, validation_alias=AliasChoices("athletes"))


class TeamWicketDetails(CCBaseModel):
    """The description of how a wicket fell."""

    text: str
    short_text: str


class TeamWicket(CCBaseModel):
    """A wicket that fell in an over, with the dismissed batter's innings."""

    details: TeamWicketDetails
    balls_faced: int
    dismissal_card: str
    fours: int
    fow: str
    minutes: int | str | None = None  # TODO: Can be empty string - parse to null in that case
    number: int
    over: float
    runs: int
    short_text: str
    sixes: int
    strike_rate: float | str


class TeamOver(CCBaseModel):
    """An over in a Team's innings, with any wickets that fell in it."""

    number: int
    runs: int
    wicket: list[TeamWicket]
