from typing import Literal

from pydantic import AliasChoices, BaseModel, Field, computed_field

from pycricinfo.source_models.api.athelete import Athlete
from pycricinfo.source_models.api.common import CCBaseModel, Position
from pycricinfo.source_models.api.linescores import PlayerInningsDetails
from pycricinfo.source_models.api.team import TeamWithColorAndLogos


class MatchPlayer(CCBaseModel):
    captain: bool
    active: bool
    active_name: str
    starter: bool
    athlete: Athlete
    position: Position
    linescores: list[PlayerInningsDetails]
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


class TeamLineup(BaseModel):
    home_or_away: Literal["home", "away"] = Field(validation_alias=AliasChoices("home_or_away", "homeAway"))
    winner: bool
    team: TeamWithColorAndLogos
    players: list[MatchPlayer] = Field(validation_alias=AliasChoices("players", "roster"))
