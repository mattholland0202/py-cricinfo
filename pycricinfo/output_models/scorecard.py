from abc import ABC, abstractmethod
from typing import Optional

from prettytable import PrettyTable
from pydantic import BaseModel, Field, computed_field, model_validator

from pycricinfo.output_models.common import SNAKE_CASE_REGEX, HeaderlessTableMixin
from pycricinfo.output_models.innings import BattingInnings, BowlingInnings, PlayerInningsCommon
from pycricinfo.source_models.athelete import AthleteWithFirstAndLastName
from pycricinfo.source_models.linescores import LinescorePeriod
from pycricinfo.source_models.match import Match
from pycricinfo.source_models.roster import MatchPlayer, Roster
from pycricinfo.source_models.team import TeamWithColorAndLogos

# ANSI escape codes for colors
RED = "\033[31m"
RESET = "\033[0m"


class CricinfoPlayerInningsCommon(PlayerInningsCommon, ABC):
    def add_linescore_stats_as_properties(data: dict, *args) -> dict:
        """
        Add individual named stats matching supplied args to the data dictionary so they can be deserialized by Pydantic

        Parameters
        ----------
        data : dict
            The data to add keys to

        Returns
        -------
        dict
            The input data dictionary, with new keys added
        """
        linescore: LinescorePeriod = data.get("linescore")
        if not linescore:
            return data

        for name in args:
            if not isinstance(name, str):
                raise TypeError("args to this function must be strings")
            name_split = str(name).split(".")
            stat_name = name_split[1] if len(name_split) > 1 else name_split[0]
            data[SNAKE_CASE_REGEX.sub("_", stat_name).lower()] = linescore.find(name)
        return data

    def colour_row(self, row_items: list[str], colour: str) -> list[str]:
        """


        Parameters
        ----------
        row_items : list[str]
            _description_
        colour : str
            _description_

        Returns
        -------
        list[str]
            _description_
        """
        return [f"{colour}{cell}{RESET}" for cell in row_items]

    @abstractmethod
    def add_to_table(self, table: PrettyTable): ...


class CricinfoBattingInnings(BattingInnings, CricinfoPlayerInningsCommon):
    player: AthleteWithFirstAndLastName  # Could be full Athlete

    @model_validator(mode="before")
    @classmethod
    def create_batting_attributes(cls, data: dict):
        data = cls.add_linescore_stats_as_properties(
            data,
            "batting.dismissal_text",
            "runs",
            "ballsFaced",
            "notouts",
            "batting.order",
            "fours",
            "sixes",
        )
        return data

    def add_to_table(self, table: PrettyTable):
        table.add_row(
            self.colour_row(
                [
                    self.player_display,
                    self.dismissal_text,
                    f"{self.runs}{'*' if self.not_out else ''}",
                    self.balls_faced,
                    self.fours,
                    self.sixes,
                ],
                RED if self.not_out else RESET,
            )
        )


class CricinfoBowlingInnings(BowlingInnings, CricinfoPlayerInningsCommon):
    player: AthleteWithFirstAndLastName  # Could be full Athlete

    @model_validator(mode="before")
    @classmethod
    def create_bowling_attributes(cls, data: dict):
        return cls.add_linescore_stats_as_properties(data, "overs", "maidens", "conceded", "wickets", "bowling.order")

    def add_to_table(self, table: PrettyTable):
        table.add_row(
            [
                self.player.display_name,
                self.overs_display,
                self.maidens,
                self.runs,
                self.wickets,
            ]
        )


class Innings(BaseModel, HeaderlessTableMixin):
    number: int
    team: TeamWithColorAndLogos
    batting_score: int
    wickets: int
    batting_description: str
    batters: list[CricinfoBattingInnings] = Field(default_factory=list)
    bowlers: list[CricinfoBowlingInnings] = Field(default_factory=list)

    @computed_field
    @property
    def score_summary(self) -> str:
        wickets_text = f" {self.batting_description}" if self.batting_description == "all out" else f"/{self.wickets}"
        return f"{self.batting_score}{wickets_text}"

    def to_table(self):
        self.print_headerless_table(
            [
                (
                    f"Innings {self.number}: {self.team.display_name} {self.score_summary}",
                    False,
                )
            ]
        )

        self._print_player_innings_table(
            ["", "Dismissal", "Runs", "Balls", "4s", "6s"],
            self.batters,
            ["", "Dismissal"],
        )

        self._print_player_innings_table(["", "Overs", "Maidens", "Runs", "Wickets"], self.bowlers)

    def _print_player_innings_table(
        self,
        field_names: list[str],
        items: list[CricinfoPlayerInningsCommon],
        field_names_to_left_align: list[str] = None,
    ):
        table = PrettyTable()
        table.field_names = field_names
        for name in field_names_to_left_align or []:
            table.align[name] = "l"

        for player in sorted(items, key=lambda b: b.order):
            player.add_to_table(table)
        print(table)


class Scorecard(BaseModel, HeaderlessTableMixin):
    title: Optional[str]
    summary: Optional[str]
    innings: list[Innings]

    @model_validator(mode="before")
    @classmethod
    def create(cls, data: dict):
        match: Match = data["match"]
        data["title"] = match.header.title
        data["summary"] = match.header.summary

        innings = []
        for i in range(1, 3 if match.header.competition.limited_overs else 5):
            team_linescore = match.header.get_batting_linescore_for_period(i)
            innings.append(
                Innings(
                    number=i,
                    team=team_linescore[0],
                    batting_score=team_linescore[1].runs,
                    wickets=team_linescore[1].wickets,
                    batting_description=team_linescore[1].description,
                )
            )
        for roster in match.rosters:
            cls._enrich_roster(innings, roster)

        data["innings"] = innings
        return data

    @classmethod
    def _enrich_roster(cls, innings: list[Innings], roster: Roster):
        for player in roster.players:
            cls._enrich_player(innings, player)

    @classmethod
    def _enrich_player(cls, innings: list[Innings], player: MatchPlayer):
        for linescore in player.linescores:
            if bool(linescore.batted) and bool(int(linescore.batted)):
                bat = CricinfoBattingInnings(
                    player=player.athlete,
                    display_name=player.athlete.display_name,
                    captain=player.captain,
                    keeper=player.keeper,
                    linescore=linescore,
                )
                innings[linescore.period - 1].batters.append(bat)
            elif bool(linescore.bowled) and bool(int(linescore.bowled)):
                bowl = CricinfoBowlingInnings(
                    player=player.athlete, display_name=player.athlete.display_name, linescore=linescore
                )
                innings[linescore.period - 1].bowlers.append(bowl)

    def to_table(self):
        self.print_headerless_table([(self.title, True), (self.summary, False)])

        for innings in self.innings:
            innings.to_table()
