from typing import Optional

from pydantic import BaseModel, computed_field, model_validator

from pycricinfo.source_models.common import CCBaseModel
from pycricinfo.source_models.dismissal import Dismissal


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
    runs_summary: list[int | str]  # 8 values: dots, singles, twos, threes, fours, X, sixes, X
    dot_ball_percentage: int
    batting_recent: BattingRecent
    preferred_shot: Optional[PreferredShot] = None
    scoring_shots: int
    control_percentage: int
    wagonZone: list[WagonZone]  # 8 zones: clockwise from long leg
    wagon: Wagon

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
