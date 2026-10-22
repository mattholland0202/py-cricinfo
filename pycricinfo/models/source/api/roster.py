"""Models for a Team's lineup in a match."""

from typing import Literal

from pydantic import AliasChoices, BaseModel, Field, computed_field

from pycricinfo.models.source.api.athelete import Athlete
from pycricinfo.models.source.api.common import CCBaseModel, Position
from pycricinfo.models.source.api.innings import PlayerInningsDetails
from pycricinfo.models.source.api.team import TeamWithColorAndLogos


class MatchPlayer(CCBaseModel):
    """A Player in a Team's lineup for a match, with their innings in that match."""

    captain: bool
    active: bool
    active_name: str
    starter: bool
    athlete: Athlete
    position: Position
    innings: list[PlayerInningsDetails] = Field(validation_alias=AliasChoices("innings", "linescores"))
    subbed_in: bool
    subbed_out: bool

    @computed_field
    @property
    def athlete_name(self) -> str:
        """The Player's display name."""
        return self.athlete.display_name

    @computed_field
    @property
    def keeper(self) -> bool:
        """Whether the Player is the wicketkeeper."""
        return self.position.abbreviation == "WK"


class TeamLineup(BaseModel):
    """A Team's lineup for a match."""

    home_or_away: Literal["home", "away"] = Field(validation_alias=AliasChoices("home_or_away", "homeAway"))
    winner: bool
    team: TeamWithColorAndLogos
    players: list[MatchPlayer] = Field(validation_alias=AliasChoices("players", "roster"))
