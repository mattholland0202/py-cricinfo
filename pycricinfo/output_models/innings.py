from abc import ABC
from typing import Optional

from pydantic import AliasChoices, BaseModel, Field, computed_field


class PlayerInningsCommon(BaseModel, ABC):
    order: int


class BattingInnings(PlayerInningsCommon):
    display_name: str
    dismissal_text: str
    captain: Optional[bool] = None
    keeper: Optional[bool] = None
    runs: int
    balls_faced: Optional[int] = None
    fours: Optional[int] = None
    sixes: Optional[int] = None
    not_out: bool = Field(validation_alias=AliasChoices("not_out", "notouts"))

    @computed_field
    @property
    def player_display(self) -> str:
        return f"{self.display_name}{' (c)' if self.captain else ''}{' \u271d' if self.keeper else ''}"


class BowlingInnings(PlayerInningsCommon):
    display_name: str
    overs: float | int
    maidens: int
    runs: int = Field(validation_alias=AliasChoices("runs", "conceded"))
    wickets: int

    @computed_field
    @property
    def overs_display(self) -> float | int:
        return int(self.overs) if self.overs % 1 == 0 else self.overs
