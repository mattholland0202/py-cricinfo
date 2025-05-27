from typing import Literal

from pydantic import AliasChoices, BaseModel, Field, computed_field

from pycricinfo.source_models.athelete import Athlete
from pycricinfo.source_models.common import CCBaseModel, Position
from pycricinfo.source_models.linescores import LinescorePeriod
from pycricinfo.source_models.team import TeamWithColorAndLogos


class MatchPlayer(CCBaseModel):
    captain: bool
    active: bool
    active_name: str
    starter: bool
    athlete: Athlete
    position: Position
    linescores: list[LinescorePeriod]
    subbedIn: bool
    subbedOut: bool

    @computed_field
    @property
    def athlete_name(self) -> str:
        return self.athlete.display_name

    @computed_field
    @property
    def keeper(self) -> bool:
        return self.position.abbreviation == "WK"


class Roster(BaseModel):
    home_or_away: Literal["home", "away"] = Field(validation_alias=AliasChoices("home_or_away", "homeAway"))
    winner: bool
    team: TeamWithColorAndLogos
    players: list[MatchPlayer] = Field(validation_alias=AliasChoices("players", "roster"))
