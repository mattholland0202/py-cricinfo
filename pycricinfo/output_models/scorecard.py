from abc import ABC
from typing import Optional

from pydantic import BaseModel, model_validator

from pycricinfo.output_models.common import SNAKE_CASE_REGEX, HeaderlessTableMixin
from pycricinfo.output_models.innings import BattingInnings, BowlingInnings, Innings, PlayerInningsCommon
from pycricinfo.source_models.api.athelete import AthleteWithFirstAndLastName
from pycricinfo.source_models.api.linescores import LinescorePeriod
from pycricinfo.source_models.api.match import Match
from pycricinfo.source_models.api.roster import MatchPlayer, Roster
from pycricinfo.source_models.api.team import TeamWithColorAndLogos


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


class CricinfoBowlingInnings(BowlingInnings, CricinfoPlayerInningsCommon):
    player: AthleteWithFirstAndLastName  # Could be full Athlete

    @model_validator(mode="before")
    @classmethod
    def create_bowling_attributes(cls, data: dict):
        return cls.add_linescore_stats_as_properties(data, "overs", "maidens", "conceded", "wickets", "bowling.order")


class CricinfoInnings(Innings):
    team: TeamWithColorAndLogos


class Scorecard(BaseModel, HeaderlessTableMixin):
    title: Optional[str]
    summary: Optional[str]
    innings: list[Innings]

    def to_table(self):
        self.print_headerless_table([(self.title, True), (self.summary, False)])

        for innings in self.innings:
            innings.to_table()


class CricinfoScorecard(Scorecard):
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
                CricinfoInnings(
                    number=i,
                    team=team_linescore[0],
                    team_name=team_linescore[0].display_name,
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
    def _enrich_roster(cls, innings: list[CricinfoInnings], roster: Roster):
        for player in roster.players:
            cls._enrich_player(innings, player)

    @classmethod
    def _enrich_player(cls, innings: list[CricinfoInnings], player: MatchPlayer):
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
