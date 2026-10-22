"""Models for a Player's career statistics, scraped from Statsguru."""

from abc import ABC

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, model_validator

from pycricinfo.types import MatchTypeNames


class CareerStatsBaseModel(BaseModel, ABC):
    """Abstract base class for a row of a Player's career statistics in one format."""

    format: MatchTypeNames
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

    @model_validator(mode="before")
    @classmethod
    def normalize_empty_values(cls, data: dict) -> dict:
        """
        Replace "-" cells, which Statsguru uses for no value, with None.

        Parameters
        ----------
        data : dict
            The table cells for the row, keyed by column header

        Returns
        -------
        dict
            The data, with "-" values replaced
        """
        if not data:
            return data

        for key, value in data.items():
            if isinstance(value, str) and value.strip() == "-":
                data[key] = None

        return data


class CareerBattingRow(CareerStatsBaseModel):
    """A Player's career batting statistics in one format."""

    matches: int | None = Field(default=None, validation_alias=AliasChoices("Mat", "mat"))
    innings: int | None = Field(default=None, validation_alias=AliasChoices("Inns", "inns"))
    not_outs: int | None = Field(default=None, validation_alias=AliasChoices("NO", "no"))
    runs: int | None = Field(default=None, validation_alias=AliasChoices("Runs", "runs"))
    highest_score: str | None = Field(
        default=None,
        validation_alias=AliasChoices("HS", "hs"),
        description="The highest career score, which is a string as it may include a '*' to indicate not out",
    )
    average: float | None = Field(default=None, validation_alias=AliasChoices("Ave", "ave"))
    balls_faced: int | None = Field(default=None, validation_alias=AliasChoices("BF", "bf"))
    strike_rate: float | None = Field(default=None, validation_alias=AliasChoices("SR", "sr"))
    centuries: int | None = Field(default=None, validation_alias=AliasChoices("100", "100s", "hundreds"))
    half_centuries: int | None = Field(default=None, validation_alias=AliasChoices("50", "50s", "fifties"))
    fours: int | None = Field(default=None, validation_alias=AliasChoices("4s"))
    sixes: int | None = Field(default=None, validation_alias=AliasChoices("6s"))
    ducks: int | None = Field(default=None, validation_alias=AliasChoices("0", "ducks"))


class CareerFieldingRow(CareerStatsBaseModel):
    """A Player's career fielding statistics in one format."""

    catches: int | None = Field(default=None, validation_alias=AliasChoices("Ct", "ct"))
    stumpings: int | None = Field(default=None, validation_alias=AliasChoices("St", "st"))
    dismissals: int | None = Field(default=None, validation_alias=AliasChoices("Dis"))
    catches_as_keeper: int | None = Field(
        default=None, validation_alias=AliasChoices("Ct Wk", "ct_wk", "catches_as_keeper")
    )
    catches_as_fielder: int | None = Field(
        default=None, validation_alias=AliasChoices("Ct Fi", "ct_fi", "catches_as_fielder")
    )


class CareerBowlingRow(CareerStatsBaseModel):
    """A Player's career bowling statistics in one format."""

    format: MatchTypeNames
    matches: int | None = Field(default=None, validation_alias=AliasChoices("Mat", "mat"))
    innings: int | None = Field(default=None, validation_alias=AliasChoices("Inns", "inns"))
    runs_conceded: int | None = Field(default=None, validation_alias=AliasChoices("Runs", "runs"))
    wickets: int | None = Field(default=None, validation_alias=AliasChoices("Wkts", "wkts"))
    best_bowling_innings: str | None = Field(default=None, validation_alias=AliasChoices("BBI", "bbi"))
    best_bowling_match: str | None = Field(default=None, validation_alias=AliasChoices("BBM", "bbm"))
    average: float | None = Field(default=None, validation_alias=AliasChoices("Ave", "ave"))
    economy_rate: float | None = Field(default=None, validation_alias=AliasChoices("Econ", "econ"))
    strike_rate: float | None = Field(default=None, validation_alias=AliasChoices("SR", "sr"))
    five_wicket_hauls: int | None = Field(default=None, validation_alias=AliasChoices("5", "5w", "five_w"))
    ten_wicket_hauls: int | None = Field(default=None, validation_alias=AliasChoices("10", "10w", "ten_w"))
    overs: str | None = Field(default=None, validation_alias=AliasChoices("Overs", "overs"))
    maidens: int | None = Field(default=None, validation_alias=AliasChoices("Mdns", "mdns", "maidens"))


class Career(BaseModel):
    """A Player's career batting, bowling and fielding statistics, with one row per format."""

    batting: list[CareerBattingRow]
    bowling: list[CareerBowlingRow]
    fielding: list[CareerFieldingRow]
