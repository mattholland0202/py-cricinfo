from typing import Optional

from pydantic import Field

from pycricinfo.models.source.api.athelete import Athlete
from pycricinfo.models.source.api.common import CCBaseModel, FlagMixin, Position, RefMixin


class PlayerRelation(CCBaseModel):
    athlete: RefMixin
    relation: str


class Player(Athlete):
    date_of_birth: str
    date_of_death: Optional[str] = Field(default=None)
    active: bool
    gender: str
    position: Position
    country: int
    relations: list[PlayerRelation]
    major_teams: list[RefMixin]
    debuts: list[RefMixin]
    flag: FlagMixin
