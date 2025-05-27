from abc import ABC

from pydantic import AliasChoices, Field

from pycricinfo.source_models.common import CCBaseModel, Event, NameMixin, RefMixin


class TeamCommon(CCBaseModel, ABC):
    id: str
    abbreviation: str
    display_name: str


class TeamWithName(TeamCommon, NameMixin): ...


class TeamWithColorAndLogos(TeamCommon):
    color: str
    logos: list[RefMixin]


class TeamFull(TeamWithName):
    color: str
    nickname: str
    short_display_name: str
    is_national: bool
    is_active: bool
    classes: list[int]
    current_match: Event = Field(default=None, validation_alias=AliasChoices("event"))
    current_players_link: RefMixin = Field(default=None, validation_alias=AliasChoices("athletes"))
