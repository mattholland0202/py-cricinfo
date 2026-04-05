from abc import ABC
from datetime import datetime
from typing import Literal, Optional

from pydantic import AliasChoices, BaseModel, Field, computed_field

from pycricinfo.models.source.api.common import CCBaseModel, Link, MatchClass, RefMixin
from pycricinfo.models.source.api.innings import TeamInningsDetails
from pycricinfo.models.source.api.league import League
from pycricinfo.models.source.api.match_note import MatchNote
from pycricinfo.models.source.api.official import Official
from pycricinfo.models.source.api.roster import TeamLineup
from pycricinfo.models.source.api.team import TeamWithColorAndLogos
from pycricinfo.models.source.api.venue import Venue


class MatchCompetitorCommon(CCBaseModel, ABC):
    """Common fields for a competitor in a match, used in both the basic and full match data models"""

    id: int
    order: int
    winner: bool
    home_or_away: Literal["home", "away"] = Field(validation_alias=AliasChoices("home_or_away", "homeAway"))


class MatchCompetitor(MatchCompetitorCommon):
    """The detailed information about a competitor in a match, as used in the match summary endpoint"""

    team: TeamWithColorAndLogos
    score: str = Field(
        description="One or two innings scores for the team, sometimes including the overs",
        examples=["421/5d", "150 & 130 (50.3 ov)"],
    )
    innings: list[TeamInningsDetails] = Field(validation_alias=AliasChoices("innings", "linescores"))


class MatchCompetitorBasic(MatchCompetitorCommon):
    """The basic information about a competitor in a match, as used in the 'event' endpoint"""

    team: RefMixin
    score: RefMixin
    innings: RefMixin = Field(validation_alias=AliasChoices("innings", "linescores"))
    roster: RefMixin
    leaders: RefMixin
    statistics: RefMixin
    record: RefMixin


class MatchCompetitonCommon(CCBaseModel, ABC):
    """Common fields for a match competition, used in both the basic and full match data models"""

    id: int = Field(description="The Cricinfo ID for the match", examples=["1225249"])
    limited_overs: bool
    reduced_overs: bool
    date: datetime = Field(description="The start date and time of the match in UTC", examples=["2024-07-26T10:00:00Z"])
    end_date: Optional[datetime] = Field(
        default=None, description="The end date and time of the match in UTC", examples=["2024-07-30T16:00:00Z"]
    )
    match_class: MatchClass = Field(validation_alias=AliasChoices("match_class", "class"))
    description: str = Field(description="Match description, covering match number in series", examples=["3rd Test"])


class MatchStatus(CCBaseModel):
    """The status of a match, as used in the match summary endpoint"""

    summary: str = Field(description="A summary of the result of the match", examples=["England won by 5 wickets"])


class MatchCompetiton(MatchCompetitonCommon):
    """The detailed information about the 'competition' in a match, as used in the match summary endpoint"""

    status: MatchStatus
    competitors: list[MatchCompetitor]


class MatchCompetitionBasic(MatchCompetitonCommon):
    """The basic information about the 'competition' in a match, as used in the 'event' endpoint"""

    short_description: str = Field(
        description="A short description of the match, which is usually actually longer than the description",
        examples=["Only Test, (D/N) at Perth"],
    )
    day_night: bool
    venue: Venue
    competitors: list[MatchCompetitorBasic]
    status: RefMixin


class MatchHeaderAndBasicCommon(CCBaseModel, ABC):
    """Common fields for match data, used in both the basic model and the header section of the full model"""

    id: int = Field(description="The Cricinfo ID for the match", examples=["1381212"])
    name: str = Field(description="The two teams competing in the match", examples=["West Indies v India"])
    short_name: str = Field(
        description="A short version of the two teams competing in the match", examples=["WI v IND"]
    )
    description: str = Field(description="Should match the 'title' field")


class MatchHeader(MatchHeaderAndBasicCommon):
    """
    The header section of the match summary endpoint in the Site API,
    which contains some basic information about the match and links to more details.
    """

    competitions: list[MatchCompetiton] = Field(
        description="Details of the competition/match. There is always only 1 item."
    )
    links: list[Link] = Field(description="Links related to the match")
    leagues: list[League] = Field(description="The league(s) that this match is part of")

    @computed_field
    @property
    def competition(self) -> MatchCompetiton:
        """Source data has a list of competitions, but in reality there is only ever 1, so return it"""
        return self.competitions[0]

    def get_batting_innings_by_number(
        self, innings_number: int
    ) -> Optional[tuple[TeamWithColorAndLogos, TeamInningsDetails]]:
        """
        Get the batting innings data for a specific innings number.

        Parameters
        ----------
        innings_number : int
            The innings number to retrieve.

        Returns
        -------
        Optional[tuple[TeamWithColorAndLogos, TeamInningsDetails]]
            The team and innings details for the specified innings number, or None if not found.
        """
        for competitor in self.competition.competitors:
            for team_innings in competitor.innings:
                if team_innings.period == innings_number and team_innings.is_batting:
                    return competitor.team, team_innings


class MatchBasic(MatchHeaderAndBasicCommon):
    """
    The response from the 'event' endpoint in the Core API.
    A simplified version of a match, containing only the most basic information and links to more details.
    """

    short_description: str = Field(
        description="More abbreviated version of the match description, without dates",
        examples=["West Indies tour of England, 3rd Test, at Manchester"],
    )
    season: RefMixin = Field(description="An API link to the Season this match was in")
    season_type: RefMixin = Field(description="An API link to the type of Season this match was in")
    venues: list[RefMixin] = Field(
        description="A list of API links to Venues for this match, practically only ever of length 1"
    )
    competitions: list[MatchCompetitionBasic] = Field(description="A list of competitions in this match")


class MatchInfo(BaseModel):
    """Information about the match, including venue, attendance and officials"""

    venue: Venue
    attendance: Optional[int] = None
    officials: list[Official]


class Match(CCBaseModel):
    """
    The response from the match summary endpoint in the Site API.
    A much more detailed version of a match, containing information about the teams, players, innings and more.
    """

    notes: list[MatchNote]
    game_info: MatchInfo
    rosters: list[TeamLineup]
    header: MatchHeader

    @computed_field
    @property
    def teams(self) -> list[MatchCompetitor]:
        return self.header.competition.competitors

    @computed_field
    @property
    def start_date(self) -> datetime:
        return self.header.competition.date

    @computed_field
    @property
    def is_international(self) -> bool:
        return self.header.competition.match_class.international_class_id is not None

    @computed_field
    @property
    def summary(self) -> bool:
        """A summary of the result of the match, e.g.) 'England won by 5 wickets'"""
        return self.header.competitions[0].status.summary
