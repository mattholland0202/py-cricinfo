from abc import ABC
from typing import Optional

from pydantic import BaseModel, computed_field

from pycricinfo.source_models.api.batting import BattingDetails
from pycricinfo.source_models.api.bowling import BowlingDetails
from pycricinfo.source_models.api.common import CCBaseModel
from pycricinfo.source_models.api.team import TeamOver


class BasicStatistic(CCBaseModel):
    name: str
    display_value: Optional[str] = None
    value: int | str | float


class StatsCategory(BaseModel):
    name: str
    stats: list[BasicStatistic]

    batting_stat_names: list[str] = [
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

    bowling_stat_names: list[str] = [
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

    team_stat_names: list[str] = [
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

    def get_stat(self, name: str) -> int | str | float:
        return next((s.value for s in self.stats if s.name == name), None)


class StatisticsCategory(ABC, BaseModel):
    id: str
    name: str
    abbreviation: str
    categories: list[StatsCategory]

    @computed_field
    @property
    def general_category(self) -> StatsCategory:
        first = next(iter(self.categories), None)
        return first

    def find(self, name: str) -> int | str | float:
        return self.general_category and self.general_category.get_stat(name)


class PlayerStatisticsCategory(StatisticsCategory):
    batting: Optional[BattingDetails] = None
    bowling: Optional[BowlingDetails] = None

    def find(self, name: str) -> int | str | float:
        split: list[str] = name.split(".")
        if len(split) == 1:
            return self.general_category and self.general_category.get_stat(name)

        if split[0] == ("batting"):
            return self.batting and getattr(self.batting, split[1])

        if split[0] == ("bowling"):
            return self.bowling and getattr(self.bowling, split[1])


class TeamStatisticsCategory(StatisticsCategory):
    overs: list[list[TeamOver]]
