from typing import Optional

from pydantic import Field

from pycricinfo.source_models.athelete import Athlete
from pycricinfo.source_models.common import Position, RefMixin


class Player(Athlete):
    date_of_birth: str
    date_of_death: Optional[str] = Field(default=None)
    active: bool
    gender: str
    position: Position
    country: int
    major_teams: list[RefMixin]
    debuts: list[RefMixin]
