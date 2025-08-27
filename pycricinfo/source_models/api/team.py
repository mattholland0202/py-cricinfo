from abc import ABC
from typing import Optional

from pydantic import AliasChoices, Field

from pycricinfo.source_models.api.common import CCBaseModel, Event, RefMixin


class TeamCommon(CCBaseModel, ABC):
    id: str
    abbreviation: str
    display_name: str


class TeamWithName(TeamCommon):
    name: str = Field(description="The full name of the Team")


class TeamWithColorAndLogos(TeamCommon):
    color: str = Field(description="The hex colour for the Team", examples=["#790d1a"])
    logos: list[RefMixin]


class TeamFull(TeamWithName):
    color: str
    nickname: str
    short_display_name: str
    is_national: bool
    is_active: bool
    classes: list[int] = Field(description="The classes of match that this Team plays in")
    current_match: Event = Field(default=None, validation_alias=AliasChoices("event"))
    current_players_link: RefMixin = Field(default=None, validation_alias=AliasChoices("athletes"))


class TeamWicketDetails(CCBaseModel):
    text: str
    short_text: str


class TeamWicket(CCBaseModel):
    details: TeamWicketDetails
    balls_faced: int
    dismissal_card: str
    fours: int
    fow: str
    minutes: Optional[int | str] = None  # TODO: Can be empty string - parse to null in that case
    number: int
    over: float
    runs: int
    short_text: str
    sixes: int
    strike_rate: float


class TeamOver(CCBaseModel):
    number: int
    runs: int
    wicket: list[TeamWicket]
