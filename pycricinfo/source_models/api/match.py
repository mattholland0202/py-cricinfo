from typing import Literal, Optional

from pydantic import AliasChoices, BaseModel, Field, computed_field

from pycricinfo.source_models.api.common import CCBaseModel
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
    score: str
    linescores: list[TeamInningsDetails]
    home_or_away: Literal["home", "away"] = Field(validation_alias=AliasChoices("home_or_away", "homeAway"))


class MatchStatus(CCBaseModel):
    summary: str


class MatchCompetiton(CCBaseModel):
    status: MatchStatus
    competitors: list[MatchCompetitor]
    limited_overs: bool


class MatchHeader(CCBaseModel):
    id: int
    name: str
    description: str
    short_name: str
    title: str
    competitions: list[MatchCompetiton]
    # TODO: links
    # TODO: leagues

    @computed_field
    @property
    def summary(self) -> bool:
        return self.competitions[0].status.summary

    @computed_field
    @property
    def competition(self) -> MatchCompetiton:
        return self.competitions[0]

    def get_batting_linescore_for_period(self, period: int) -> tuple[TeamWithColorAndLogos, TeamInningsDetails]:
        for competitor in self.competition.competitors:
            for linescore in competitor.linescores:
                if linescore.period == period and linescore.is_batting:
                    return competitor.team, linescore


class MatchInfo(BaseModel):
    venue: Venue
    attendance: Optional[int] = None
    officials: list[Official]


class Match(CCBaseModel):
    notes: list[MatchNote]
    game_info: MatchInfo
    # TODO: add debuts
    rosters: list[TeamLineup]
    header: MatchHeader
