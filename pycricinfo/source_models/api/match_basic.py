from pydantic import AliasChoices, Field

from pycricinfo.source_models.api.common import CCBaseModel, MatchClass, RefMixin
from pycricinfo.source_models.api.venue import Venue


class MatchCompetitorBasic(CCBaseModel):
    id: int
    winner: bool
    home_or_away: str = Field(validation_alias=AliasChoices("home_or_away", "homeAway"))
    team: RefMixin
    score: RefMixin
    linescores: RefMixin
    roster: RefMixin
    leaders: RefMixin
    statistics: RefMixin
    record: RefMixin


class MatchCompetitionBasic(CCBaseModel):
    id: int
    description: str
    date: str
    end_date: str
    day_night: bool
    limited_overs: bool
    reduced_overs: bool
    match_class: MatchClass = Field(validation_alias=AliasChoices("match_class", "class"))
    venue: Venue
    competitors: list[MatchCompetitorBasic]


class MatchBasic(CCBaseModel):
    id: int
    name: str
    description: str
    short_name: str
    short_description: str
    season: RefMixin
    season_type: RefMixin
    venues: list[RefMixin]
    competitions: list[MatchCompetitionBasic]
