from abc import ABC
from typing import Literal, Optional

from pydantic import AliasChoices, BaseModel, Field, computed_field, field_validator

from pycricinfo.source_models.api.athelete import Athlete
from pycricinfo.source_models.api.common import CCBaseModel, RefMixin
from pycricinfo.source_models.api.statistics import PlayerStatisticsCategory, StatisticsCategory, TeamStatisticsCategory


class BaseInningsDetails(CCBaseModel, ABC):
    period: int
    statistics: StatisticsCategory

    def find(self, name: str) -> int | str | float:
        return self.statistics.find(name)


class PlayerInningsDetails(BaseInningsDetails):
    media_id: int = Field(validation_alias=AliasChoices("media_id", "mediaId"))
    statistics: PlayerStatisticsCategory

    @computed_field
    @property
    def batted(self) -> bool:
        return self.find("batted")

    @computed_field
    @property
    def bowled(self) -> bool:
        return self.find("bowled")


class PartnershipBatter(CCBaseModel):
    athlete: Athlete
    balls: str | int
    runs: str | int


class InningsState(BaseModel):
    overs: str | float
    runs: str | int
    wickets: str | int


class PartnershipFallOfWicketCommon(RefMixin, CCBaseModel, ABC):
    wicket_number: int
    fow_type: Literal["out", "end of innings", "not out", "retired not out"]
    runs: int

    @field_validator('fow_type', mode='before')
    @classmethod
    def strip_fow_type(cls, v):
        """
        In source data, fow_type has trailing whitespace on "retired not out", so trim it before validation.
        """
        if isinstance(v, str):
            return v.strip()
        return v


class Partnership(PartnershipFallOfWicketCommon):
    wicket_name: str
    overs: float
    run_rate: float
    start: InningsState
    end: InningsState
    batsmen: list[PartnershipBatter]


class FallOfWicket(PartnershipFallOfWicketCommon):
    wicket_over: float
    runs_scored: int
    balls_faced: int
    athlete: Athlete


class TeamInningsDetails(BaseInningsDetails):
    wickets: int
    runs: int
    overs: float
    is_batting: bool
    fours: Optional[int] = None
    sixes: Optional[int] = None
    description: str
    target: int
    follow_on: int
    statistics: Optional[TeamStatisticsCategory]
    partnerships: Optional[list[Partnership]] = None
    fall_of_wicket: Optional[list[FallOfWicket]] = Field(
        default=None, validation_alias=AliasChoices("fall_of_wicket", "fow")
    )

    @computed_field
    @property
    def declared(self) -> bool:
        return self.description.lower() == "declared"
