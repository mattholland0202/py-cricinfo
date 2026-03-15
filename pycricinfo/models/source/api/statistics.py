from abc import ABC
from typing import Optional

from pydantic import BaseModel, Field, computed_field

from pycricinfo.models.source.api.batting import BattingDetails
from pycricinfo.models.source.api.bowling import BowlingDetails
from pycricinfo.models.source.api.common import CCBaseModel
from pycricinfo.models.source.api.team import TeamOver

BATTING_STAT_NAMES: list[str] = [
    "ballsFaced",
    "batted",
    "battingPosition",
    "dismissal",
    "dismissalCard",
    "ducks",
    "fielderKeeper",
    "fielderSub",
    "fiftyPlus",
    "fours",
    "hundreds",
    "innings",
    "inningsNumber",
    "minutes",
    "notouts",
    "outs",
    "retiredDescription",
    "runs",
    "sixes",
    "strikeRate",
]
""" All possible names of statistics within a batting innings """

BOWLING_STAT_NAMES: list[str] = [
    "balls",
    "bowled",
    "bowlingPosition",
    "bpo",
    "caught",
    "caughtFielder",
    "caughtKeeper",
    "conceded",
    "dismissals",
    "dots",
    "economyRate",
    "fielded",
    "fiveWickets",
    "fourPlusWickets",
    "foursConceded",
    "illegalOverLimit",
    "inningsBowled",
    "inningsFielded",
    "inningsNumber",
    "maidens",
    "noballs",
    "overs",
    "sixesConceded",
    "stumped",
    "tenWickets",
    "wickets",
    "wides",
]
""" All possible names of statistics within a bowling innings """

TEAM_STAT_NAMES: list[str] = [
    "ballLimit",
    "balls",
    "bpo",
    "byes",
    "extras",
    "lead",
    "legbyes",
    "liveCurrent",
    "minutes",
    "miscounted",
    "noballs",
    "oldPenaltyOrBonus",
    "overLimit",
    "overLimitRunRate",
    "overSplitLimit",
    "overs",
    "oversDocked",
    "penalties",
    "penaltiesFieldEnd",
    "penaltiesFieldStart",
    "runRate",
    "runs",
    "target",
    "targetachievedMinutes",
    "targetachievedOvers",
    "targetachievedRuns",
    "targetachievedWickets",
    "wickets",
    "wides",
]
""" All possible names of statistics within an overall Team innings """


class BasicStatistic(CCBaseModel):
    """
    Details of a single statistic entry, such as balls bowled or runs scored
    """

    name: str = Field(
        description=(
            "The name of this statistic. One of the values from BATTING_STAT_NAMES, "
            "BOWLING_STAT_NAMES or TEAM_STAT_NAMES"
        )
    )
    display_value: Optional[str] = Field(
        default=None, description="How this value should be displayed, if different from the raw value itself"
    )
    value: int | str | float = Field(
        description="The actual value of the statistic, with the type varying as appropriate"
    )


class StatsCategory(BaseModel):
    """
    A category of statistics
    """

    name: str = Field(description="The name of this group of statistics, such as 'general', 'batting' or 'bowling'")
    stats: list[BasicStatistic] = Field(description="The list of stats in this category")

    def get_stat(self, name: str) -> Optional[int | str | float]:
        """
        Find a matching stat within this category

        Parameters
        ----------
        name : str
            The name of the stat to find

        Returns
        -------
        Optional[int | str | float]
            The value of the matching stat, if found, otherwise None
        """
        return next((s.value for s in self.stats if s.name == name), None)


class StatsCategoryContainer(ABC, BaseModel):
    """
    A container for a category of statistics, because source data nests this to an extra level, and in theory there
    could be more than one category of stats, although in practice this never seems to be the case. This layer of
    model isn't really needed.
    """

    id: str = Field(description="The ID of this container of stats categories, which seems to always be 0")
    name: str = Field(description="The name of this container of stats categories, which seems to always be 'Total'")
    abbreviation: str = Field(
        description="The abbreviation of this container of stats categories, which seems to always be 'Total'"
    )
    categories: list[StatsCategory] = Field(
        description="The list of stats categories, which in practice seems to only ever contain one entry"
    )

    @computed_field
    @property
    def first_category(self) -> StatsCategory:
        """The first category in this container"""
        first = next(iter(self.categories), None)
        return first

    def find(self, name: str) -> Optional[int | str | float]:
        """
        Find a matching stat within the first category

        Parameters
        ----------
        name : str
            The name of the stat to find

        Returns
        -------
        Optional[int | str | float]
            The value of the matching stat, if found, otherwise None
        """
        return self.first_category and self.first_category.get_stat(name)


class PlayerStatisticsCategoryContainer(StatsCategoryContainer):
    """
    A container for a category of statistics specific to a Player's innings, adding optional properties for batting or
    bowling depending on the innings type
    """

    batting: Optional[BattingDetails] = Field(
        default=None,
        description="Extra statistics representing a batting innings, such as shot locations and runs breakdown",
    )
    bowling: Optional[BowlingDetails] = Field(
        default=None,
        description="Extra statistics representing a bowling innings, such as delivery pitch map details",
    )

    def find(self, name: str) -> Optional[int | str | float]:
        """
        Find a statistic, either within the primary category from the base container, or by the matching attribute
        within the batting or bowling extensions

        Parameters
        ----------
        name : str
            The name of the stat to find. Just a name if searching within the primary base container, otherwise starting
            with "batting." or "bowling." to search in those extensions

        Returns
        -------
        Optional[int | str | float]
            The value of the matching stat, if found, otherwise None
        """
        split: list[str] = name.split(".")
        if len(split) == 1:
            return super().find(name)

        if split[0] == ("batting"):
            return self.batting and getattr(self.batting, split[1])

        if split[0] == ("bowling"):
            return self.bowling and getattr(self.bowling, split[1])


class TeamStatisticsCategory(StatsCategoryContainer):
    """
    A container for a category of statistics specific to a Team's innings, adding an optional property for Overs
    """

    overs: list[list[TeamOver]] = Field(
        description=(
            "The breakdown of overs in the innings. Source data is a list of lists, outer always seems "
            "to be of length 1."
        )
    )
