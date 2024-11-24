import re
from abc import ABC, abstractmethod
from typing import Optional

from prettytable import PrettyTable
from pydantic import AliasChoices, BaseModel, Field, computed_field, model_validator

from cricinfo.source_models.athelete import Athlete
from cricinfo.source_models.linescores import LinescorePeriod
from cricinfo.source_models.match import Match
from cricinfo.source_models.roster import Player, Roster
from cricinfo.source_models.team import Team

# ANSI escape codes for colors
RED = "\033[31m"
RESET = "\033[0m"

SNAKE_CASE_REGEX = re.compile(r'(?<!^)(?=[A-Z])')

class HeaderlessTableMixin():
    def print_headerless_table(self, rows: list[tuple[str, bool]]):
        table = PrettyTable()
        table.header = False
        for row in rows:
            table.add_row([row[0]], divider=row[1])
        print(table)


class PlayerInningsModel(BaseModel, ABC):
    order: int

    def add_linescore_stats_as_properties(data: dict, *args):
        linescore: LinescorePeriod = data.get("linescore")
        if not linescore:
            return data
        
        for name in args:
            name_split = str(name).split('.')
            stat_name = name_split[1] if len(name_split) > 1 else name_split[0]
            data[SNAKE_CASE_REGEX.sub('_', stat_name).lower()] = linescore.gs(name)
        return data
    
    def colour_row(self, row_items: list[str], colour: str) -> list[str]:
        return [f"{colour}{cell}{RESET}" for cell in row_items]
    
    @abstractmethod
    def add_to_table(self, table: PrettyTable): ...

class BattingInnings(PlayerInningsModel):
    player: Athlete
    dismissal_text: str
    captain: bool
    keeper: bool
    runs: int
    balls_faced: Optional[int] = None
    fours: Optional[int] = None
    sixes: Optional[int] = None
    not_out: bool = Field(validation_alias=AliasChoices('not_out', 'notouts'))

    @computed_field
    @property
    def player_display(self) -> str:
        return f"{self.player.display_name}{' (c)' if self.captain else ''}{' \u271D' if self.keeper else ''}"

    @model_validator(mode='before')
    @classmethod
    def create_batting_attributes(cls, data: dict):
        data = cls.add_linescore_stats_as_properties(data, "batting.dismissal_text", "runs", "ballsFaced", "notouts", "batting.order", "fours", "sixes")
        return data
    
    def add_to_table(self, table: PrettyTable):
        table.add_row(self.colour_row([self.player_display, 
                                       self.dismissal_text,
                                       f"{self.runs}{"*" if self.not_out else ''}", 
                                       self.balls_faced,
                                       self.fours,
                                       self.sixes], 
                                       RED if self.not_out else RESET))

class BowlingInnings(PlayerInningsModel):
    player: Athlete
    overs: float|int
    maidens: int
    runs: int = Field(validation_alias=AliasChoices('runs', 'conceded'))
    wickets: int

    @computed_field
    @property
    def overs_display(self) -> float|int:
        return int(self.overs) if self.overs % 1 == 0 else self.overs

    @model_validator(mode='before')
    @classmethod
    def create_bowling_attributes(cls, data: dict):
        return cls.add_linescore_stats_as_properties(data, "overs", "maidens", "conceded", "wickets", "bowling.order")

    def add_to_table(self, table: PrettyTable):
        table.add_row([self.player.display_name, self.overs_display, self.maidens, self.runs, self.wickets])

class Innings(BaseModel, HeaderlessTableMixin):
    number: int
    team: Team
    batting_score: int
    wickets: int
    batting_description: str
    batters: list[BattingInnings] = []
    bowlers: list[BowlingInnings] = []

    @computed_field
    @property
    def score_summary(self) -> bool:
        wickets_text = f" {self.batting_description}" if self.batting_description == "all out" else f"/{self.wickets}"
        return f"{self.batting_score}{wickets_text}"

    def to_table(self):
        self.print_headerless_table([(f"Innings {self.number}: {self.team.display_name} {self.score_summary}", False)])

        self._print_player_innings_table(["", "Dismissal", "Runs", "Balls", "4s", "6s"],
                                         self.batters, ["", "Dismissal"])
        
        self._print_player_innings_table(["", "Overs", "Maidens", "Runs", "Wickets"],
                                         self.bowlers, [""])

    def _print_player_innings_table(self, field_names: list[str], items: list[PlayerInningsModel],
                                   field_names_to_left_align: list[str]):
        table = PrettyTable()
        table.field_names = field_names
        for name in field_names_to_left_align:
            table.align[name] = "l"

        for batter in sorted(items, key=lambda b: b.order):
            batter.add_to_table(table)
        print(table)
    
class Scorecard(BaseModel, HeaderlessTableMixin):
    title: Optional[str]
    summary: Optional[str]
    innings: list[Innings]

    @model_validator(mode='before')
    @classmethod
    def create(cls, data: dict):
        match: Match = data["match"]
        data["title"] = match.header.title
        data["summary"] = match.header.summary

        innings = []
        for i in range(1,5):
            team_linescore = match.header.get_batting_linescore_for_period(i)
            innings.append(Innings(number=i, 
                                   team=team_linescore[0],
                                   batting_score=team_linescore[1].runs, 
                                   wickets=team_linescore[1].wickets,
                                   batting_description=team_linescore[1].description))
        for roster in match.rosters:
            cls._enrich_roster(innings, roster)
        
        data["innings"] = innings
        return data

    @classmethod
    def _enrich_roster(cls, innings: list[Innings], roster: Roster):
        for player in roster.players:
            cls._enrich_player(innings, player)

    @classmethod
    def _enrich_player(cls, innings: list[Innings], player: Player):
        for linescore in player.linescores:
            if bool(linescore.batted) and bool(int(linescore.batted)):
                bat = BattingInnings(player=player.athlete,
                                     captain=player.captain,
                                     keeper=player.keeper,
                                     linescore=linescore)
                innings[linescore.period-1].batters.append(bat)
            elif bool(linescore.bowled) and bool(int(linescore.bowled)):
                bowl = BowlingInnings(player=player.athlete,
                                      linescore=linescore)
                innings[linescore.period-1].bowlers.append(bowl)

    def to_table(self):
        self.print_headerless_table([(self.title, True), (self.summary, False)])

        for innings in self.innings:
            innings.to_table()