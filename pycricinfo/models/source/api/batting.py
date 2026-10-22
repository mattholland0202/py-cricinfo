"""Models for a Player's batting innings."""

from pydantic import BaseModel, Field, computed_field, model_validator

from pycricinfo.models.source.api.common import CCBaseModel
from pycricinfo.models.source.api.dismissal import Dismissal


class BattingRecent(CCBaseModel):
    """Runs and balls faced by a batter over a recent span of overs."""

    balls: int
    over_span: int
    runs: int


class PreferredShot(CCBaseModel):
    """The shot a batter scored most with in their innings."""

    shot_name: str
    runs_summary: list[int]
    balls_faced: int
    runs: int


class BattingPvp(CCBaseModel):
    """Player-versus-player (pvp) runs and balls for a batter."""

    balls: int
    runs: int


class WagonZone(CCBaseModel):
    """Runs scored by a batter in one zone of the wagon wheel."""

    runs_summary: list[int]
    scoring_shots: int
    runs: int


class Wagon(BaseModel):
    """A batter's wagon wheel, with each zone named, clockwise from long leg."""

    long_leg: WagonZone
    backward_square_leg: WagonZone
    mid_wicket: WagonZone
    mid_on: WagonZone
    mid_off: WagonZone
    cover: WagonZone
    backward_point: WagonZone
    third: WagonZone


class BattingDetails(CCBaseModel):
    """Extended details of a Player's batting innings."""

    active: bool
    active_name: str
    order: int
    out_details: Dismissal
    pvp: BattingPvp
    runs_summary: list[int | str] = Field(
        description="Count of number of deliveries of each possible run count. Will be 8 elements: 0,1,2,3,4,5,6,7",
        max_length=8,
    )
    dot_ball_percentage: int
    batting_recent: BattingRecent
    preferred_shot: PreferredShot | None = None
    scoring_shots: int | None = Field(default=None, description="Number of scoring shots in the innings")
    control_percentage: int | None = Field(
        default=None,
        description="Percentage of deliveries where the batter played a controlled shot",
    )
    wagon_zone: list[WagonZone] | None = Field(
        default=None, description="Raw data of list of wagon areas, clockwise from long leg", max_length=8
    )
    wagon: Wagon | None = Field(
        default=None,
        description=(
            "Processed Wagon object containing details of named wagon zones, only present if wagonZone field "
            "is present in the API response"
        ),
    )

    @computed_field
    @property
    def dismissal_text(self) -> str | None:
        """How the batter was dismissed, with the wicketkeeper's dagger symbol shown as a cross."""
        return self.out_details and self.out_details.short_text.replace("&dagger;", "\u271d").strip()

    @model_validator(mode="before")
    @classmethod
    def generate_wagon(cls, data: dict) -> dict:
        """
        Generate a Wagon object from the raw wagonZone data in the API response, if present.

        The wagonZone data is a list of 8 elements, corresponding to the 8 wagon zones in clockwise order from long
        leg.

        Parameters
        ----------
        data : dict
            The raw data for a batting innings

        Returns
        -------
        dict
            The data with the Wagon added, if the wagonZone data was present
        """
        wagon_fields = Wagon.model_fields.keys()

        wagon_zone = data.get("wagonZone")
        if wagon_zone:
            wagon = dict(zip(wagon_fields, wagon_zone, strict=True))
            data["wagon"] = Wagon(**wagon)

        return data
