from pydantic import BaseModel, computed_field
from typing import Optional

from cricinfo.source_models import MatchNote, Official, Roster, Venue, CCBaseModel, Team, Ref

class TeamWicketDetails(CCBaseModel):
    text: str
    short_text: str

class TeamWicket(CCBaseModel):
    details: TeamWicketDetails
    balls_faced: int
    dismissal_card: str
    fours: int
    fow: str
    minutes: int
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

class TeamLinescoreStatistics(CCBaseModel):
    name: str
    overs: list[list[TeamOver]]
    # TODO: Add categories

class TeamLinescore(CCBaseModel):
    period: int
    wickets: int
    runs: int
    overs: float
    is_batting: bool
    description: str
    target: int
    statistics: Optional[TeamLinescoreStatistics]
    # TODO: add partnerships
    # TODO: add fow

class MatchCompetitor(CCBaseModel):
    id: int
    winner: bool
    team: Team
    score: str
    linescores: list[TeamLinescore]

class MatchStatus(CCBaseModel):
    summary: str

class MatchCompetiton(CCBaseModel):
    status: MatchStatus
    competitors: list[MatchCompetitor]

class MatchHeader(CCBaseModel):
    id: int
    name: str
    description: str
    short_name: str
    title: str
    competitions: list[MatchCompetiton]

    @computed_field
    @property
    def summary(self) -> bool:
        return self.competitions[0].status.summary
    
    @computed_field
    @property
    def competition(self) -> MatchCompetiton:
        return self.competitions[0]
    
    def get_batting_linescore_for_period(self, period: int) -> tuple[Team, TeamLinescore]:
        for competitor in self.competition.competitors:
            for linescore in competitor.linescores:
                if linescore.period == period and linescore.is_batting:
                    return competitor.team, linescore

class MatchInfo(BaseModel):
    venue: Venue
    attendance: int
    officials: list[Official]

class Match(CCBaseModel):
    notes: list[MatchNote]
    game_info: MatchInfo
    # TODO: add debuts
    rosters: list[Roster]
    header: MatchHeader