from typing import Optional

from pydantic import BaseModel, Field, computed_field, model_validator

from pycricinfo.models.source.api.common import CCBaseModel
from pycricinfo.models.source.api.dismissal import Dismissal


class BattingRecent(CCBaseModel):
    balls: int
    over_span: int
    runs: int


class PreferredShot(CCBaseModel):
    shot_name: str
    runs_summary: list[int]
    balls_faced: int
    runs: int


class BattingPvp(CCBaseModel):
    balls: int
    runs: int


class WagonZone(CCBaseModel):
    runs_summary: list[int]
    scoring_shots: int
    runs: int


class Wagon(BaseModel):
    long_leg: WagonZone
    backward_square_leg: WagonZone
    mid_wicket: WagonZone
    mid_on: WagonZone
    mid_off: WagonZone
    cover: WagonZone
    backward_point: WagonZone
    third: WagonZone


class BattingDetails(CCBaseModel):
    active: bool
    active_name: str
    order: int
    out_details: Dismissal
    pvp: BattingPvp
    runs_summary: list[int | str] = Field(
        description="Count of number of deliveries for each possible run count. Will be 8 elements: 0,1,2,3,4,5,6,7",
        max_length=8,
    )
    dot_ball_percentage: int
    batting_recent: BattingRecent
    preferred_shot: Optional[PreferredShot] = None
    scoring_shots: Optional[int] = Field(default=None, description="Number of scoring shots in the innings")
    control_percentage: Optional[int] = Field(
        default=None,
        description="Percentage of deliveries where the batter played a controlled shot",
    )
    wagon_zone: Optional[list[WagonZone]] = Field(
        default=None, description="Raw data of list of wagon areas, clockwise from long leg", max_length=8
    )
    wagon: Optional[Wagon] = Field(
        default=None,
        description=(
            "Processed Wagon object containing details of named wagon zones, only present if wagonZone field "
            "is present in the API response"
        ),
    )

    @computed_field
    @property
    def dismissal_text(self) -> Optional[str]:
        return self.out_details and self.out_details.short_text.replace("&dagger;", "\u271d").strip()

    @model_validator(mode="before")
    @classmethod
    def generate_wagon(cls, data: dict):
        wagon_fields = Wagon.model_fields.keys()

        wagon_zone = data.get("wagonZone", None)
        if wagon_zone:
            wagon = dict(zip(wagon_fields, wagon_zone))
            data["wagon"] = Wagon(**wagon)

        return data
