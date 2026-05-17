from typing import Optional

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, model_validator

from pycricinfo.types import MatchTypeNames


class CareerStatsBaseModel(BaseModel):
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


class CareerBattingFieldingRow(CareerStatsBaseModel):
    format: MatchTypeNames
    matches: Optional[int] = Field(default=None, validation_alias="mat")
    innings: Optional[int] = Field(default=None, validation_alias="inns")
    not_outs: Optional[int] = Field(default=None, validation_alias="no")
    runs: Optional[int] = Field(default=None)
    highest_score: Optional[str] = Field(
        default=None,
        validation_alias="hs",
        description="The highest career score, which is a string as it may include a '*' to indicate not out",
    )
    average: Optional[float] = Field(default=None, validation_alias="ave")
    balls_faced: Optional[int] = Field(default=None, validation_alias="bf")
    strike_rate: Optional[float] = Field(default=None, validation_alias="sr")
    centuries: Optional[int] = Field(default=None, validation_alias=AliasChoices("100s", "hundreds"))
    half_centuries: Optional[int] = Field(default=None, validation_alias=AliasChoices("50s", "fifties"))
    fours: Optional[int] = Field(default=None, validation_alias="4s")
    sixes: Optional[int] = Field(default=None, validation_alias="6s")
    catches: Optional[int] = Field(default=None, validation_alias="ct")
    stumpings: Optional[int] = Field(default=None, validation_alias="st")
    ducks: Optional[int] = Field(default=None, validation_alias=AliasChoices("0", "ducks"))
    dismissals: Optional[int] = Field(default=None)
    catches_as_keeper: Optional[int] = Field(default=None, validation_alias=AliasChoices("ct_wk", "catches_as_keeper"))
    catches_as_fielder: Optional[int] = Field(
        default=None, validation_alias=AliasChoices("ct_fi", "catches_as_fielder")
    )


class CareerBowlingRow(CareerStatsBaseModel):
    format: MatchTypeNames
    matches: Optional[int] = Field(default=None, validation_alias="mat")
    innings: Optional[int] = Field(default=None, validation_alias="inns")
    balls_bowled: Optional[int] = Field(default=None, validation_alias="balls")
    runs_conceded: Optional[int] = Field(default=None, validation_alias="runs")
    wickets: Optional[int] = Field(default=None, validation_alias="wkts")
    best_bowling_innings: Optional[str] = Field(default=None, validation_alias="bbi")
    best_bowling_match: Optional[str] = Field(default=None, validation_alias="bbm")
    average: Optional[float] = Field(default=None, validation_alias="ave")
    economy_rate: Optional[float] = Field(default=None, validation_alias="econ")
    strike_rate: Optional[float] = Field(default=None, validation_alias="sr")
    four_wicket_hauls: Optional[int] = Field(default=None, validation_alias=AliasChoices("4w", "four_w"))
    five_wicket_hauls: Optional[int] = Field(default=None, validation_alias=AliasChoices("5w", "five_w"))
    ten_wicket_hauls: Optional[int] = Field(default=None, validation_alias=AliasChoices("10w", "ten_w"))
    overs: Optional[str] = Field(default=None)
    maidens: Optional[int] = Field(default=None, validation_alias=AliasChoices("mdns", "maidens"))


class Career(BaseModel):
    batting_and_fielding: list[CareerBattingFieldingRow]
    bowling: list[CareerBowlingRow]
