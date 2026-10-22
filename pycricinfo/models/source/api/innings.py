"""Models for Team and Player innings."""

from abc import ABC
from typing import Literal

from pydantic import AliasChoices, BaseModel, Field, computed_field, field_validator

from pycricinfo.models.source.api.athelete import Athlete
from pycricinfo.models.source.api.common import CCBaseModel, RefMixin
from pycricinfo.models.source.api.statistics import (
    PlayerStatisticsCategoryContainer,
    StatsCategoryContainer,
    TeamStatisticsCategory,
)


class BaseInningsDetails(CCBaseModel, ABC):
    """Abstract base class for common fields between a Team's Innings and individual Player innings."""

    period: int = Field(description="Which period of the match this Innings is")
    statistics: StatsCategoryContainer = Field(
        description="The stats category container for this innings. Expected to be overridden by Player or Team stats"
    )

    def find(self, name: str) -> int | str | float | None:
        """
        Find a matching stat within the attached category.

        Parameters
        ----------
        name : str
            The name of the stat to find. Just a name if searching within the primary base container, otherwise (if in
            a Player innings) starting with "batting." or "bowling." to search in those extensions

        Returns
        -------
        int | str | float | None
            The value of the matching stat, if found, otherwise None
        """
        return self.statistics.find(name)


class PlayerInningsDetails(BaseInningsDetails):
    """A Player's innings in a match, covering both their batting and bowling."""

    media_id: int = Field(description="A media ID for this innings")
    statistics: PlayerStatisticsCategoryContainer

    @computed_field
    @property
    def batted(self) -> bool:
        """Whether the Player batted in this innings."""
        batted = self.find("batted")
        return bool(batted) and bool(int(batted))

    @computed_field
    @property
    def absent(self) -> bool:
        """Whether the Player was absent and so did not bat."""
        return self.find("absentDescription") == "absent"

    @computed_field
    @property
    def retired_hurt(self) -> bool:
        """Whether the Player retired hurt."""
        return (not self.absent) and self.find("retiredDescription") == "hurt"

    @computed_field
    @property
    def is_batting_innings(self) -> bool:
        """Whether this innings should appear in the batting scorecard: the Player batted, or was absent."""
        return self.batted or self.absent

    @computed_field
    @property
    def bowled(self) -> bool:
        """Whether the Player bowled in this innings."""
        bowled = self.find("bowled")
        return bool(bowled) and bool(int(bowled))


class PartnershipBatter(CCBaseModel):
    """A batter's contribution to a partnership."""

    athlete: Athlete
    balls: str | int
    runs: str | int


class InningsState(BaseModel):
    """The score of an innings at a point in time."""

    overs: str | float
    runs: str | int
    wickets: str | int


class PartnershipFallOfWicketCommon(RefMixin, CCBaseModel, ABC):
    """Abstract base class for common fields between a Partnership and a Fall of Wicket."""

    wicket_number: int = Field(description="Which number wicket in the innings this was")
    fow_type: Literal["out", "end of innings", "not out", "retired not out"] = Field(
        description="Which of the fixed values for a wicket falling this represents"
    )
    runs: int = Field(description="The number of runs scored at this current point")

    @field_validator("fow_type", mode="before")
    @classmethod
    def strip_fow_type(cls, v: object) -> object:
        """
        Trim whitespace from fow_type before validation.

        In source data, fow_type has trailing whitespace on "retired not out".

        Parameters
        ----------
        v : object
            The raw fow_type value

        Returns
        -------
        object
            The value, trimmed if it is a string
        """
        if isinstance(v, str):
            return v.strip()
        return v


class Partnership(PartnershipFallOfWicketCommon):
    """A partnership between two batters."""

    wicket_name: str
    overs: float
    run_rate: float
    start: InningsState
    end: InningsState
    batsmen: list[PartnershipBatter]


class FallOfWicket(PartnershipFallOfWicketCommon):
    """The score when a wicket fell, and the batter who was out."""

    wicket_over: float
    runs_scored: int
    balls_faced: int
    athlete: Athlete


class TeamInningsDetails(BaseInningsDetails):
    """A Team's innings in a match."""

    wickets: int
    runs: int
    overs: float
    is_batting: bool
    fours: int | None = None
    sixes: int | None = None
    description: str
    target: int
    follow_on: int
    statistics: TeamStatisticsCategory | None
    partnerships: list[Partnership] | None = None
    fall_of_wicket: list[FallOfWicket] | None = Field(
        default=None, validation_alias=AliasChoices("fall_of_wicket", "fow")
    )

    @computed_field
    @property
    def declared(self) -> bool:
        """Whether the innings was declared."""
        return self.description.lower() == "declared"
