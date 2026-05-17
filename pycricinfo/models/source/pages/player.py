from abc import ABC
from typing import Optional

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, model_validator

from pycricinfo.types import MatchTypeNames


class CareerStatsBaseModel(BaseModel, ABC):
    format: MatchTypeNames
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

    @model_validator(mode="before")
    @classmethod
    def normalize_empty_values(cls, data: dict):
        if not data:
            return data

        for key, value in data.items():
            if isinstance(value, str) and value.strip() == "-":
                data[key] = None

        return data


class CareerBattingRow(CareerStatsBaseModel):
    matches: Optional[int] = Field(default=None, validation_alias=AliasChoices("Mat", "mat"))
    innings: Optional[int] = Field(default=None, validation_alias=AliasChoices("Inns", "inns"))
    not_outs: Optional[int] = Field(default=None, validation_alias=AliasChoices("NO", "no"))
    runs: Optional[int] = Field(default=None, validation_alias=AliasChoices("Runs", "runs"))
    highest_score: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("HS", "hs"),
        description="The highest career score, which is a string as it may include a '*' to indicate not out",
    )
    average: Optional[float] = Field(default=None, validation_alias=AliasChoices("Ave", "ave"))
    balls_faced: Optional[int] = Field(default=None, validation_alias=AliasChoices("BF", "bf"))
    strike_rate: Optional[float] = Field(default=None, validation_alias=AliasChoices("SR", "sr"))
    centuries: Optional[int] = Field(default=None, validation_alias=AliasChoices("100", "100s", "hundreds"))
    half_centuries: Optional[int] = Field(default=None, validation_alias=AliasChoices("50", "50s", "fifties"))
    fours: Optional[int] = Field(default=None, validation_alias=AliasChoices("4s"))
    sixes: Optional[int] = Field(default=None, validation_alias=AliasChoices("6s"))
    ducks: Optional[int] = Field(default=None, validation_alias=AliasChoices("0", "ducks"))


class CareerFieldingRow(CareerStatsBaseModel):
    catches: Optional[int] = Field(default=None, validation_alias=AliasChoices("Ct", "ct"))
    stumpings: Optional[int] = Field(default=None, validation_alias=AliasChoices("St", "st"))
    dismissals: Optional[int] = Field(default=None, validation_alias=AliasChoices("Dis"))
    catches_as_keeper: Optional[int] = Field(
        default=None, validation_alias=AliasChoices("Ct Wk", "ct_wk", "catches_as_keeper")
    )
    catches_as_fielder: Optional[int] = Field(
        default=None, validation_alias=AliasChoices("Ct Fi", "ct_fi", "catches_as_fielder")
    )


class CareerBowlingRow(CareerStatsBaseModel):
    format: MatchTypeNames
    matches: Optional[int] = Field(default=None, validation_alias=AliasChoices("Mat", "mat"))
    innings: Optional[int] = Field(default=None, validation_alias=AliasChoices("Inns", "inns"))
    balls_bowled: Optional[int] = Field(default=None, validation_alias=AliasChoices("Balls", "balls"))
    runs_conceded: Optional[int] = Field(default=None, validation_alias=AliasChoices("Runs", "runs"))
    wickets: Optional[int] = Field(default=None, validation_alias=AliasChoices("Wkts", "wkts"))
    best_bowling_innings: Optional[str] = Field(default=None, validation_alias=AliasChoices("BBI", "bbi"))
    best_bowling_match: Optional[str] = Field(default=None, validation_alias=AliasChoices("BBM", "bbm"))
    average: Optional[float] = Field(default=None, validation_alias=AliasChoices("Ave", "ave"))
    economy_rate: Optional[float] = Field(default=None, validation_alias=AliasChoices("Econ", "econ"))
    strike_rate: Optional[float] = Field(default=None, validation_alias=AliasChoices("SR", "sr"))
    four_wicket_hauls: Optional[int] = Field(default=None, validation_alias=AliasChoices("4w", "Four", "four_w"))
    five_wicket_hauls: Optional[int] = Field(default=None, validation_alias=AliasChoices("5", "5w", "five_w"))
    ten_wicket_hauls: Optional[int] = Field(default=None, validation_alias=AliasChoices("10", "10w", "ten_w"))
    overs: Optional[str] = Field(default=None, validation_alias=AliasChoices("Overs", "overs"))
    maidens: Optional[int] = Field(default=None, validation_alias=AliasChoices("Mdns", "mdns", "maidens"))


class Career(BaseModel):
    batting: list[CareerBattingRow]
    bowling: list[CareerBowlingRow]
    fielding: list[CareerFieldingRow]
