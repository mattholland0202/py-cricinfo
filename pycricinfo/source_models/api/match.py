from datetime import datetime
from typing import Literal, Optional

from pydantic import AliasChoices, BaseModel, Field, computed_field

from pycricinfo.source_models.api.common import CCBaseModel, Link, MatchClass
from pycricinfo.source_models.api.league import League
from pycricinfo.source_models.api.linescores import TeamInningsDetails
from pycricinfo.source_models.api.match_note import MatchNote
from pycricinfo.source_models.api.official import Official
from pycricinfo.source_models.api.roster import TeamLineup
from pycricinfo.source_models.api.team import TeamWithColorAndLogos
from pycricinfo.source_models.api.venue import Venue


class MatchCompetitor(CCBaseModel):
    id: int
    winner: bool
    team: TeamWithColorAndLogos
    score: str = Field(
        description="One or two innings scores for the team, sometimes including the overs",
        examples=["421/5d", "150 & 130 (50.3 ov)"],
    )
    innings: list[TeamInningsDetails] = Field(validation_alias=AliasChoices("innings", "linescores"))
    home_or_away: Literal["home", "away"] = Field(validation_alias=AliasChoices("home_or_away", "homeAway"))


class MatchStatus(CCBaseModel):
    summary: str = Field(description="A summary of the result of the match", examples=["England won by 5 wickets"])


class MatchCompetiton(CCBaseModel):
    status: MatchStatus
    competitors: list[MatchCompetitor]
    limited_overs: bool
    reduced_overs: bool
    match_class: MatchClass = Field(validation_alias=AliasChoices("match_class", "class"))
    date: datetime = Field(description="The start date and time of the match in UTC", examples=["2024-07-26T10:00:00Z"])
    end_date: Optional[datetime] = Field(
        default=None, description="The end date and time of the match in UTC", examples=["2024-07-30T16:00:00Z"]
    )


class MatchHeader(CCBaseModel):
    id: int = Field(description="The Cricinfo ID for the match", examples=["1381212"])
    name: str = Field(description="The two teams competing in the match", examples=["West Indies v India"])
    short_name: str = Field(
        description="A short version of the two teams competing in the match", examples=["WI v IND"]
    )
    title: str = Field(
        description="A full title for the match, including teams, series, venue and dates",
        examples=["3rd Test, West Indies tour of England at Birmingham, Jul 26-28 2024"],
    )
    description: str = Field(description="Should match the 'title' field")
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
            for linescore in competitor.innings:
                if linescore.period == innings_number and linescore.is_batting:
                    return competitor.team, linescore


class MatchInfo(BaseModel):
    venue: Venue
    attendance: Optional[int] = None
    officials: list[Official]


class Match(CCBaseModel):
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
