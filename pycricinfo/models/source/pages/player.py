from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CareerStatsBaseModel(BaseModel):
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class CareerBattingFieldingRow(CareerStatsBaseModel):
    format: str
    matches: Optional[str] = Field(default=None, validation_alias="mat")
    innings: Optional[str] = Field(default=None, validation_alias="inns")
    not_outs: Optional[str] = Field(default=None, validation_alias="no")
    runs: Optional[str] = None
    highest_score: Optional[str] = Field(default=None, validation_alias="hs")
    average: Optional[str] = Field(default=None, validation_alias="ave")
    balls_faced: Optional[str] = Field(default=None, validation_alias="bf")
    strike_rate: Optional[str] = Field(default=None, validation_alias="sr")
    centuries: Optional[str] = Field(default=None, validation_alias="hundreds")
    half_centuries: Optional[str] = Field(default=None, validation_alias="fifties")
    fours: Optional[str] = None
    sixes: Optional[str] = None
    catches: Optional[str] = Field(default=None, validation_alias="ct")
    stumpings: Optional[str] = Field(default=None, validation_alias="st")


class CareerBowlingRow(CareerStatsBaseModel):
    format: str
    matches: Optional[str] = Field(default=None, validation_alias="mat")
    innings: Optional[str] = Field(default=None, validation_alias="inns")
    balls_bowled: Optional[str] = Field(default=None, validation_alias="balls")
    runs_conceded: Optional[str] = Field(default=None, validation_alias="runs")
    wickets: Optional[str] = Field(default=None, validation_alias="wkts")
    best_bowling_innings: Optional[str] = Field(default=None, validation_alias="bbi")
    best_bowling_match: Optional[str] = Field(default=None, validation_alias="bbm")
    average: Optional[str] = Field(default=None, validation_alias="ave")
    economy_rate: Optional[str] = Field(default=None, validation_alias="econ")
    strike_rate: Optional[str] = Field(default=None, validation_alias="sr")
    four_wicket_hauls: Optional[str] = Field(default=None, validation_alias="four_w")
    five_wicket_hauls: Optional[str] = Field(default=None, validation_alias="five_w")
    ten_wicket_hauls: Optional[str] = Field(default=None, validation_alias="ten_w")


class Career(BaseModel):
    batting_and_fielding: list[CareerBattingFieldingRow]
    bowling: list[CareerBowlingRow]
