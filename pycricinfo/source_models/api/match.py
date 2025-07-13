import re
from typing import Literal, Optional

from pydantic import AliasChoices, BaseModel, Field, computed_field, model_validator

from pycricinfo.source_models.api.athelete import Athlete
from pycricinfo.source_models.api.common import CCBaseModel, RefMixin
from pycricinfo.source_models.api.match_note import MatchNote
from pycricinfo.source_models.api.official import Official
from pycricinfo.source_models.api.roster import TeamLineup
from pycricinfo.source_models.api.statistics import TeamStatisticsCategory
from pycricinfo.source_models.api.team import TeamWithColorAndLogos
from pycricinfo.source_models.api.venue import Venue


class PartnershipBatter(CCBaseModel):
    athlete: Athlete
    balls: str | int
    runs: str | int


class InningsState(BaseModel):
    overs: str | float
    runs: str | int
    wickets: str | int


class Partnership(RefMixin, CCBaseModel):
    wicket_number: int
    wicket_name: str
    fow_type: Literal["out", "end of innings"]
    overs: float
    runs: int
    run_rate: float
    start: InningsState
    end: InningsState
    batsmen: list[PartnershipBatter]


class FallOfWicket(RefMixin, CCBaseModel):
    wicket_number: int
    wicket_over: float
    fow_type: Literal["out", "end of innings"]
    runs: int
    runs_scored: int
    balls_faced: int
    athlete: Athlete


SNAKE_CASE_REGEX = re.compile(r"(?<!^)(?=[A-Z])")


class TeamLinescore(CCBaseModel):
    period: int
    wickets: int
    runs: int
    overs: float
    is_batting: bool
    fours: Optional[int] = None
    sixes: Optional[int] = None
    description: str
    target: int
    follow_on: int
    statistics: Optional[TeamStatisticsCategory]
    partnerships: Optional[list[Partnership]] = None
    fall_of_wicket: Optional[list[FallOfWicket]] = Field(
        default=None, validation_alias=AliasChoices("fall_of_wicket", "fow")
    )

    extras: Optional[str] = None
    byes: Optional[str] = None
    wides: Optional[str] = None
    legbyes: Optional[str] = None
    noballs: Optional[str] = None
    penalties: Optional[str] = None

    def add_linescore_stats_as_properties(data: dict, *args) -> dict:
        """
        Add items to the data dictionary so that extra keys can be deserialized into the Pydantic model.

        Find items by looking up the strings passed in as arguments, either matching to keys in the player's
        "general" statistics list for this innings, or to other parsed items in their batting or bowling innings.

        Parameters
        ----------
        data : dict
            The data to add keys to

        Returns
        -------
        dict
            The input data dictionary, with new keys added
        """
        stats_dict: dict = data.get("statistics")
        if not stats_dict:
            return data

        stats = TeamStatisticsCategory.model_validate(stats_dict)

        for name in args:
            if not isinstance(name, str):
                raise TypeError("args to this function must be strings")
            name_split = str(name).split(".")
            stat_name = name_split[1] if len(name_split) > 1 else name_split[0]

            value = stats.find(name)
            if value is not None:
                data[SNAKE_CASE_REGEX.sub("_", stat_name).lower()] = value
        return data

    @model_validator(mode="before")
    @classmethod
    def create_additional_attributes(cls, data: dict) -> dict:
        data = cls.add_linescore_stats_as_properties(
            data,
            "bpo"
            "byes",
            "extras",
            "legbyes",
            "noballs",
            "penalties",
            "runRate",
            "wides",
        )
        return data


class MatchCompetitor(CCBaseModel):
    id: int
    winner: bool
    team: TeamWithColorAndLogos
    score: str
    linescores: list[TeamLinescore]
    home_or_away: Literal["home", "away"] = Field(validation_alias=AliasChoices("home_or_away", "homeAway"))


class MatchStatus(CCBaseModel):
    summary: str


class MatchCompetiton(CCBaseModel):
    status: MatchStatus
    competitors: list[MatchCompetitor]
    limited_overs: bool


class MatchHeader(CCBaseModel):
    id: int
    name: str
    description: str
    short_name: str
    title: str
    competitions: list[MatchCompetiton]
    # TODO: links
    # TODO: leagues

    @computed_field
    @property
    def summary(self) -> bool:
        return self.competitions[0].status.summary

    @computed_field
    @property
    def competition(self) -> MatchCompetiton:
        return self.competitions[0]

    def get_batting_linescore_for_period(self, period: int) -> tuple[TeamWithColorAndLogos, TeamLinescore]:
        for competitor in self.competition.competitors:
            for linescore in competitor.linescores:
                if linescore.period == period and linescore.is_batting:
                    return competitor.team, linescore


class MatchInfo(BaseModel):
    venue: Venue
    attendance: Optional[int] = None
    officials: list[Official]


class Match(CCBaseModel):
    notes: list[MatchNote]
    game_info: MatchInfo
    # TODO: add debuts
    rosters: list[TeamLineup]
    header: MatchHeader


class MatchBasic(CCBaseModel):
    id: int
    name: str
    description: str
    short_name: str
    short_description: str
    season: RefMixin
    season_type: RefMixin
    venues: list[RefMixin]
