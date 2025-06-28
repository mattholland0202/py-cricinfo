from abc import ABC, abstractmethod
from typing import Optional

from prettytable import PrettyTable
from pydantic import AliasChoices, BaseModel, Field, computed_field, model_validator

from pycricinfo.output_models.common import SNAKE_CASE_REGEX, HeaderlessTableMixin
from pycricinfo.source_models.api.athelete import AthleteWithFirstAndLastName
from pycricinfo.source_models.api.linescores import PlayerMatchInningsDetails
from pycricinfo.source_models.api.team import TeamWithColorAndLogos

# ANSI escape codes for colors
RED = "\033[31m"
RESET = "\033[0m"


class PlayerInningsCommon(BaseModel, ABC):
    order: int

    def colour_row(self, row_items: list[str], colour: str) -> list[str]:
        """
        Change the colour of a row in a PrettyTable.

        Parameters
        ----------
        row_items : list[str]
            Each cell in the row to be coloured.
        colour : str
            The ANSI escape code for the desired colour.

        Returns
        -------
        list[str]
            The row items with the specified colour applied.
        """
        return [f"{colour}{cell}{RESET}" for cell in row_items]

    @abstractmethod
    def add_to_table(self, table: PrettyTable): ...


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
        """
        Get the batting scorecard display name of the player, including captain and keeper status.

        Returns
        -------
        str
            The player's display name, with captain and keeper indicators if applicable.
        """
        return f"{self.display_name}{' (c)' if self.captain else ''}{' \u271d' if self.keeper else ''}"

    def add_to_table(self, table: PrettyTable):
        """
        Add the batting innings details as in row in a PrettyTable, colouring the row red if the player is not out.

        Parameters
        ----------
        table : PrettyTable
            The PrettyTable instance to which the row will be added.
        """
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


class BowlingInnings(PlayerInningsCommon):
    display_name: str
    overs: float | int
    maidens: int
    runs: int = Field(validation_alias=AliasChoices("runs", "conceded"))
    wickets: int

    @computed_field
    @property
    def overs_display(self) -> float | int:
        """
        Round the overs to an integer if they are a whole number (to remove any '.0' on the end),
        otherwise return as a float.

        Returns
        -------
        float | int
            The overs bowled, rounded to an integer if applicable.
        """
        return int(self.overs) if self.overs % 1 == 0 else self.overs

    def add_to_table(self, table: PrettyTable):
        """
        Add the bowling innings details as a row in a PrettyTable.

        Parameters
        ----------
        table : PrettyTable
            The PrettyTable instance to which the row will be added.
        """
        table.add_row(
            [
                self.display_name,
                self.overs_display,
                self.maidens,
                self.runs,
                self.wickets,
            ]
        )


class Innings(BaseModel, HeaderlessTableMixin):
    number: int
    team_name: str
    batting_score: int
    wickets: int
    batters: list[BattingInnings] = Field(default_factory=list)
    bowlers: list[BowlingInnings] = Field(default_factory=list)

    @computed_field
    @property
    def score_summary(self) -> str:
        """
        Get the score summary for the innings, including the score and wickets.

        Returns
        -------
        str
            The score summary in the format "<runs>/<wickets>" or "<runs> all out" as appropriate.
        """
        wickets_text = f" {'all out'}" if self.wickets == 10 else f"/{self.wickets}"
        return f"{self.batting_score}{wickets_text}"

    def to_table(self):
        """
        Print the innings details in PrettyTables. This will include the innings summary, followed by
        batting and bowling tables.
        """
        self.print_headerless_table(
            [
                (
                    f"Innings {self.number}: {self.team_name} {self.score_summary}",
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
        items: list[PlayerInningsCommon],
        field_names_to_left_align: list[str] = None,
    ):
        """
        Print a PrettyTable with the specified field names and items, representing either a Bowling or Batting innings.

        Parameters
        ----------
        field_names : list[str]
            The names of the fields to be displayed in the table.
        items : list[PlayerInningsCommon]
            The list of player innings items to be added to the table.
        field_names_to_left_align : list[str], optional
            Which fields in the table to align to the left (rather than the usual centre), by default None
        """
        table = PrettyTable()
        table.field_names = field_names
        for name in field_names_to_left_align or []:
            table.align[name] = "l"

        for player in sorted(items, key=lambda b: b.order):
            player.add_to_table(table)
        print(table)


class CricinfoPlayerInningsCommon(PlayerInningsCommon, ABC):
    def add_linescore_stats_as_properties(data: dict, *args) -> dict:
        """
        Add individual named stats matching supplied args to the data dictionary, so they become keys which can be
        deserialized into a Pydantic model, by matching strings passed in as arguments to keys in the player's
        statistics list for this innings.

        Parameters
        ----------
        data : dict
            The data to add keys to

        Returns
        -------
        dict
            The input data dictionary, with new keys added
        """
        linescore: PlayerMatchInningsDetails = data.get("linescore")
        if not linescore:
            return data

        for name in args:
            if not isinstance(name, str):
                raise TypeError("args to this function must be strings")
            name_split = str(name).split(".")
            stat_name = name_split[1] if len(name_split) > 1 else name_split[0]
            data[SNAKE_CASE_REGEX.sub("_", stat_name).lower()] = linescore.find(name)
        return data


class CricinfoBattingInnings(BattingInnings, CricinfoPlayerInningsCommon):
    player: AthleteWithFirstAndLastName  # Could be full Athlete

    @model_validator(mode="before")
    @classmethod
    def create_batting_attributes(cls, data: dict) -> dict:
        """
        Run before Pydantic validation to create the required fields in the data dictionary.

        Find the batting statistics in the linescore and add them as properties to the data dictionary.

        Parameters
        ----------
        data : dict
            The input data being validated into this model. It should contain a "linescore" key with a
            PlayerMatchInningsDetails object.

        Returns
        -------
        dict
            The transformed data dictionary with the required fields for a CricinfoBattingInnings, which Pydantic can
            now validate.
        """
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


class CricinfoBowlingInnings(BowlingInnings, CricinfoPlayerInningsCommon):
    player: AthleteWithFirstAndLastName  # Could be full Athlete

    @model_validator(mode="before")
    @classmethod
    def create_bowling_attributes(cls, data: dict):
        """
        Run before Pydantic validation to create the required fields in the data dictionary.

        Find the bowling statistics in the linescore and add them as properties to the data dictionary.

        Parameters
        ----------
        data : dict
            The input data being validated into this model. It should contain a "linescore" key with a
            PlayerMatchInningsDetails object.

        Returns
        -------
        dict
            The transformed data dictionary with the required fields for a CricinfoBowlingInnings, which Pydantic can
            now validate.
        """
        return cls.add_linescore_stats_as_properties(data, "overs", "maidens", "conceded", "wickets", "bowling.order")


class CricinfoInnings(Innings):
    team: TeamWithColorAndLogos
