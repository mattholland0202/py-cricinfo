from abc import ABC

from pydantic import AliasChoices, Field

from pycricinfo.source_models.api.common import CCBaseModel, Event, RefMixin


class TeamCommon(CCBaseModel, ABC):
    id: str
    abbreviation: str
    display_name: str


class TeamWithName(TeamCommon):
    name: str = Field(description="The full name of the Team")


class TeamWithColorAndLogos(TeamCommon):
    color: str
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
