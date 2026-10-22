"""Output models for innings, and the batting and bowling rows within them, built from the source models."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from prettytable import PrettyTable
from pydantic import AliasChoices, BaseModel, Field, computed_field, model_validator

from pycricinfo.models.output.common import SNAKE_CASE_REGEX, HeaderlessTableMixin
from pycricinfo.models.source.api.athelete import Athlete
from pycricinfo.models.source.api.team import TeamWithColorAndLogos

if TYPE_CHECKING:
    from pycricinfo.models.source.api.innings import BaseInningsDetails

# ANSI escape codes for colors
RED = "\033[31m"
RESET = "\033[0m"

ALL_OUT_WICKETS = 10


class InningsStatsLookupMixin(BaseModel, ABC):
    """Mixin which copies named statistics from a source innings onto the data for an output model."""

    @staticmethod
    def add_innings_stats_as_properties(data: dict, *args: str) -> dict:
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
        innings: BaseInningsDetails = data.get("innings") or data.get("player_innings")
        if not innings:
            return data

        for name in args:
            if not isinstance(name, str):
                msg = "args to this function must be strings"
                raise TypeError(msg)
            name_split = str(name).split(".")
            stat_name = name_split[1] if len(name_split) > 1 else name_split[0]

            value = innings.find(name)
            if value is not None:
                data[SNAKE_CASE_REGEX.sub("_", stat_name).lower()] = value
        return data


class PlayerInningsCommon(BaseModel, ABC):
    """Common base class shared between batting and bowling innings."""

    order: int = Field(
        description="The order within the innings that this player batted or bowled",
        validation_alias=AliasChoices("order", "batting_position", "bowling_position"),
    )
    player_id: str | int = Field(description="The unique identifier for the player in this innings")

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
    def add_to_table(self, table: PrettyTable, **kwargs: bool) -> None:
        """
        Add the innings details as a row in a PrettyTable.

        Parameters
        ----------
        table : PrettyTable
            The PrettyTable instance to which the row will be added.
        **kwargs : bool
            Options to include extra columns, which must match the columns in the table
        """


class BattingInnings(PlayerInningsCommon):
    """A row in a batting scorecard."""

    innings_id: int | None = Field(
        default=None,
        description="The unique identifier for the innings that this batting performance belongs to",
        validation_alias=AliasChoices("innings_id", "battingId", "batting_id"),
    )
    display_name: str
    dismissal_text: str
    captain: bool | None = None
    keeper: bool | None = None
    runs: int
    balls_faced: int | None = None
    fours: int | None = None
    sixes: int | None = None
    minutes: int | None = None
    not_out: bool = Field(validation_alias=AliasChoices("not_out", "notouts"))
    strike_rate: float | str | None = Field(default=None, validation_alias=AliasChoices("strike_rate", "strikeRate"))
    absent: bool | None = None
    retired_hurt: bool | None = None

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

    def add_to_table(self, table: PrettyTable, **kwargs: bool) -> None:
        """
        Add the batting innings details as a row in a PrettyTable, colouring the row red if the player is not out.

        Parameters
        ----------
        table : PrettyTable
            The PrettyTable instance to which the row will be added.
        **kwargs : bool
            include_batting_minutes: whether to add the minutes batted
        """
        row_data = [
            self.player_display,
            self.dismissal_text,
        ]

        if self.absent:
            row_data.extend(["-", "-", "-", "-"])
        else:
            row_data.extend(
                [
                    f"{self.runs}{'*' if self.not_out else ''}",
                    self.balls_faced,
                    self.fours,
                    self.sixes,
                ]
            )

        if kwargs.get("include_batting_minutes"):
            row_data.append("-") if self.absent else row_data.append(self.minutes)

        row_data.append("-") if self.absent else row_data.append(self.strike_rate)

        table.add_row(
            self.colour_row(
                row_data,
                RED if (self.not_out and not self.retired_hurt) else RESET,
            )
        )


class BowlingInnings(PlayerInningsCommon):
    """A row in a bowling scorecard."""

    innings_id: int | None = Field(
        default=None,
        description="The unique identifier for the innings that this batting performance belongs to",
        validation_alias=AliasChoices("innings_id", "bowlingId", "bowling_id"),
    )
    display_name: str
    overs: float | int
    maidens: int
    runs: int = Field(validation_alias=AliasChoices("runs", "conceded"))
    wickets: int
    dots: int | None = None
    no_balls: int | None = Field(default=None, validation_alias=AliasChoices("no_balls", "noballs"))
    wides: int | None = None
    economy_rate: float | None = Field(validation_alias=AliasChoices("economy_rate", "economyRate"))
    fours_conceded: int | None = Field(default=None, validation_alias=AliasChoices("fours_conceded", "foursConceded"))
    sixes_conceded: int | None = Field(default=None, validation_alias=AliasChoices("sixes_conceded", "sixesConceded"))

    @computed_field
    @property
    def overs_display(self) -> float | int:
        """
        Round the overs to an integer if they are a whole number, to remove any '.0' on the end.

        Otherwise, return them as a float.

        Returns
        -------
        float | int
            The overs bowled, rounded to an integer if applicable.
        """
        return int(self.overs) if self.overs % 1 == 0 else self.overs

    def add_to_table(self, table: PrettyTable, **kwargs: bool) -> None:
        """
        Add the bowling innings details as a row in a PrettyTable.

        Parameters
        ----------
        table : PrettyTable
            The PrettyTable instance to which the row will be added.
        **kwargs : bool
            include_bowling_dots: whether to add the number of dot balls
        """
        row_data = [
            self.display_name,
            self.overs_display,
            self.maidens,
            self.runs,
            self.wickets,
            self.economy_rate,
            self.no_balls,
            self.wides,
            self.fours_conceded,
            self.sixes_conceded,
        ]

        if kwargs.get("include_bowling_dots"):
            row_data.append(self.dots)

        table.add_row(row_data)


class Innings(BaseModel, HeaderlessTableMixin):
    """An innings in a scorecard, with its batting and bowling rows."""

    number: int
    batting_team_name: str
    batting_score: int
    declared: bool = Field(default=False)
    follow_on: bool = Field(default=False)
    wickets: int
    overs: float | None = None
    batters: list[BattingInnings] = Field(default_factory=list)
    bowlers: list[BowlingInnings] = Field(default_factory=list)
    extras: int | None = None
    byes: int | None = None
    wides: int | None = None
    leg_byes: int | None = Field(default=None, validation_alias=AliasChoices("legbyes", "leg_byes"))
    no_balls: int | None = Field(default=None, validation_alias=AliasChoices("noballs", "no_balls"))
    penalties: int | None = None

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
        wickets_text = f" {'all out'}" if self.wickets == ALL_OUT_WICKETS else f"/{self.wickets}"
        overs_text = f" ({self.overs} overs)" if self.overs is not None else ""

        return (
            f"{self.batting_score}{wickets_text}"
            f"{'d' if self.declared else ''}{' (f/o)' if self.follow_on else ''}"
            f"{overs_text}"
        )

    @computed_field
    @property
    def extras_summary(self) -> str:
        """
        Get a summary of the extras for the innings.

        This includes byes, leg byes, wides, no balls, and (if present) penalties.

        Returns
        -------
        str
            A string summarizing the extras in the format:
            "Extras: <extras> (<byes>b <leg_byes>lb <wides>w <no_balls>nb <penalties>p)"
        """
        penalties_string = f" {self.penalties}p" if self.penalties and self.penalties != "0" else ""

        return (
            f"Extras: {self.extras or 0} "
            f"({self.byes or 0}b {self.leg_byes or 0}lb {self.wides or 0}w {self.no_balls or 0}nb{penalties_string})"
        )

    def show(self, **kwargs: bool) -> None:
        """
        Print the innings details in PrettyTables.

        This will include the innings summary, followed by batting and bowling tables.

        Parameters
        ----------
        **kwargs : bool
            Supports parameters to customise the columns of the tables:
            - include_batting_minutes : bool
            - include_bowling_dots : bool
        """
        self.print_headerless_table(
            [
                (
                    f"Innings {self.number}: {self.batting_team_name} {self.score_summary}",
                    False,
                ),
                (
                    self.extras_summary,
                    False,
                ),
            ]
        )

        batting_field_names = ["", "Dismissal", "Runs", "Balls", "4s", "6s"]
        if kwargs.get("include_batting_minutes"):
            batting_field_names.append("Mins")
        batting_field_names.append("SR")

        self._print_player_innings_table(batting_field_names, self.batters, ["", "Dismissal"], **kwargs)

        bowling_field_names = ["", "Overs", "Maidens", "Runs", "Wickets", "Economy", "No Balls", "Wides", "4s", "6s"]
        if kwargs.get("include_bowling_dots"):
            bowling_field_names.append("Dots")

        self._print_player_innings_table(bowling_field_names, self.bowlers, [""], **kwargs)

    def _print_player_innings_table(
        self,
        field_names: list[str],
        items: list[PlayerInningsCommon],
        field_names_to_left_align: list[str] | None = None,
        **kwargs: bool,
    ) -> None:
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
        **kwargs : bool
            Options to include extra columns, passed to each row's add_to_table
        """
        table = PrettyTable()
        table.field_names = field_names
        for name in field_names_to_left_align or []:
            table.align[name] = "l"

        for player in sorted(items, key=lambda b: b.order):
            player.add_to_table(table, **kwargs)
        print(table)  # noqa: T201 - printing the table is the purpose of this method


class CricinfoBattingInnings(BattingInnings, InningsStatsLookupMixin):
    """A row in a batting scorecard, built from a Player's innings in the Cricinfo API."""

    player: Athlete

    @model_validator(mode="before")
    @classmethod
    def create_batting_attributes(cls, data: dict) -> dict:
        """
        Run before Pydantic validation to create the required fields in the data dictionary.

        Find the batting statistics in the innings and add them as properties to the data dictionary.

        Parameters
        ----------
        data : dict
            The input data being validated into this model. It should contain a "innings" key with a
            BaseInningsDetails object.

        Returns
        -------
        dict
            The transformed data dictionary with the required fields for a CricinfoBattingInnings, which Pydantic can
            now validate.
        """
        data = cls.add_innings_stats_as_properties(
            data,
            "batting.dismissal_text",
            "runs",
            "ballsFaced",
            "notouts",
            "battingPosition",
            "fours",
            "sixes",
            "minutes",
            "strikeRate",
            "battingId",
            "absentDescription",
            "retiredDescription",
        )

        if data.get("absent_description") == "absent":
            data["dismissal_text"] = "absent hurt"
        return data


class CricinfoBowlingInnings(BowlingInnings, InningsStatsLookupMixin):
    """A row in a bowling scorecard, built from a Player's innings in the Cricinfo API."""

    player: Athlete

    @model_validator(mode="before")
    @classmethod
    def create_bowling_attributes(cls, data: dict) -> dict:
        """
        Run before Pydantic validation to create the required fields in the data dictionary.

        Find the bowling statistics in the innings and add them as properties to the data dictionary.

        Parameters
        ----------
        data : dict
            The input data being validated into this model. It should contain a "innings" key with a
            BaseInningsDetails object.

        Returns
        -------
        dict
            The transformed data dictionary with the required fields for a CricinfoBowlingInnings, which Pydantic can
            now validate.
        """
        return cls.add_innings_stats_as_properties(
            data,
            "overs",
            "maidens",
            "conceded",
            "wickets",
            "bowling.order",
            "dots",
            "noballs",
            "wides",
            "foursConceded",
            "sixesConceded",
            "economyRate",
            "bowlingId",
        )


class CricinfoInnings(Innings, InningsStatsLookupMixin):
    """An innings in a scorecard, built from a Team's innings in the Cricinfo API."""

    team: TeamWithColorAndLogos

    @model_validator(mode="before")
    @classmethod
    def create_innings_attributes(cls, data: dict) -> dict:
        """
        Run before Pydantic validation to create the required fields in the data dictionary.

        Find the statistics in the innings and add them as properties to the data dictionary.

        Parameters
        ----------
        data : dict
            The input data being validated into this model. It should contain a "player_innings" key with a
            BaseInningsDetails object.

        Returns
        -------
        dict
            The transformed data dictionary with the required fields for a CricinfoInnings, which Pydantic can
            now validate.
        """
        return cls.add_innings_stats_as_properties(
            data,
            "bpo",
            "byes",
            "extras",
            "legbyes",
            "noballs",
            "penalties",
            "runRate",
            "wides",
        )
