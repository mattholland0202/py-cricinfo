from pydantic import AliasChoices, Field

from pycricinfo.models.source.api.common import CCBaseModel, DateMixin, MatchClass, RefMixin
from pycricinfo.models.source.api.venue import Venue


class MatchCompetitorBasic(CCBaseModel):
    id: int
    winner: bool
    home_or_away: str = Field(validation_alias=AliasChoices("home_or_away", "homeAway"))
    team: RefMixin
    score: RefMixin
    innings: RefMixin = Field(validation_alias=AliasChoices("innings", "linescores"))
    roster: RefMixin
    leaders: RefMixin
    statistics: RefMixin
    record: RefMixin


class MatchCompetitionBasic(DateMixin):
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
    id: int = Field(description="Cricinfo ID of the match")
    name: str = Field(description="Names of the two teams", examples=["England v West Indies"])
    short_name: str = Field(description="Short names of the two teams", examples=["ENG v WI"])
    description: str = Field(
        description="Match description, covering match number in series and fixture dates",
        examples=["3rd Test, West Indies tour of England at Manchester, Jul 24-28 2020"],
    )
    short_description: str = Field(
        description="More abbreviated version of the match description, without dates",
        examples=["West Indies tour of England, 3rd Test, at Manchester"],
    )
    season: RefMixin = Field(description="An API link to the Season this match was in")
    season_type: RefMixin = Field(description="An API link to the type of Season this match was in")
    venues: list[RefMixin] = Field(
        description="A list of API links to Venues for this match, practically only ever of length 1"
    )
    competitions: list[MatchCompetitionBasic] = Field(description="")
