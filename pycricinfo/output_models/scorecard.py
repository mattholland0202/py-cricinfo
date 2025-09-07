import html
from typing import Optional

from pydantic import BaseModel, Field, model_validator

from pycricinfo.output_models.common import HeaderlessTableMixin
from pycricinfo.output_models.innings import CricinfoBattingInnings, CricinfoBowlingInnings, CricinfoInnings, Innings
from pycricinfo.source_models.api.match import Match
from pycricinfo.source_models.api.roster import MatchPlayer, TeamLineup


class Scorecard(BaseModel, HeaderlessTableMixin):
    title: Optional[str] = Field(
        description="The title for the scorecard, usually match details, including teams"
        "and dates. e.g.) 3rd Test, West Indies tour of England at Birmingham, Jul 26-28 2024 "
    )
    summary: Optional[str] = Field(description="A summary of the result of the match, e.g.) 'India won by 5 wickets'")
    innings: list[Innings]

    def to_table(self, **kwargs):
        """
        Print the scorecard as a PrettyTable, including the title and summary.
        """
        self.print_headerless_table([(self.title, True), (self.summary, False)])

        for innings in self.innings:
            innings.to_table(**kwargs)


class CricinfoScorecard(Scorecard):
    @model_validator(mode="before")
    @classmethod
    def create(cls, data: dict) -> dict:
        """
        Run before Pydantic validation to create the required fields in the data dictionary.

        Transforms input data into a Scorecard, extracting details from a Match object.

        Parameters
        ----------
        data : dict
            The input data being validated into this model. It should contain a "match" key with a Match object.

        Raises
        ------
        ValueError
            If the "match" key is not present in the input data.

        Returns
        -------
        dict
            The transformed data dictionary with the required fields for a CricinfoScorecard, which Pydantic can
            now validate.
        """
        match: Match = data["match"]
        if not match:
            raise ValueError("Match data is required to create a CricinfoScorecard.")

        data["title"] = html.unescape(match.header.title)
        data["summary"] = html.unescape(match.summary)

        innings = []
        for i in range(1, 3 if match.header.competition.limited_overs else 5):
            response = match.header.get_batting_innings_by_number(i)
            if not response:
                continue

            team, linescore = response
            innings.append(
                CricinfoInnings(
                    number=i,
                    team=team,
                    batting_team_name=team.display_name,
                    batting_score=linescore.runs,
                    wickets=linescore.wickets,
                    overs=linescore.overs,
                    linescore=linescore,
                    declared=linescore.declared,
                    follow_on=linescore.follow_on,
                )
            )
        for roster in match.rosters:
            cls._enrich_innings_with_lineups(innings, roster)

        data["innings"] = innings
        return data

    @classmethod
    def _enrich_innings_with_lineups(cls, innings: list[CricinfoInnings], lineup: TeamLineup):
        """
        Enrich the innings with player data from the team lineup. The innings will be updated in
        place, adding batters and bowlers based on the players in the lineup.

        Parameters
        ----------
        innings : list[CricinfoInnings]
            All innings in the match, which will be enriched with player data.
        lineup : TeamLineup
            The team lineup containing player data to enrich the innings with.
        """
        for player in lineup.players:
            cls._enrich_innings_for_player(innings, player)

    @classmethod
    def _enrich_innings_for_player(cls, innings: list[CricinfoInnings], player: MatchPlayer):
        """
        Enrich the innings with data for a specific player. The innings will be updated in
        place, adding batters or bowlers records based on this player's data.

        Parameters
        ----------
        innings : list[CricinfoInnings]
            All innings in the match, which will be enriched with player data.
        player : MatchPlayer
            The player whose data will be used to enrich the innings.
        """
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
