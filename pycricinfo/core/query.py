from pycricinfo.config import BaseRoute, get_settings
from pycricinfo.output_models.scorecard import Scorecard
from pycricinfo.source_models.commentary import APIResponseCommentary, CommentaryItem
from pycricinfo.source_models.match import Match, MatchBasic
from pycricinfo.source_models.player import Player
from pycricinfo.source_models.team import TeamFull

from .api_helper import get_and_parse


def get_player(player_id: int) -> Player:
    return get_and_parse(get_settings().routes.player, Player, params={"player_id": player_id})


def get_team(team_id: int) -> TeamFull:
    # TODO: Format "classes" field onto what match type they represent
    return get_and_parse(get_settings().routes.team, TeamFull, params={"team_id": team_id})


def get_match_basic(match_id: int) -> MatchBasic:
    return get_and_parse(get_settings().routes.match_basic, MatchBasic, params={"match_id": match_id})


def get_match(match_id: int) -> Match:
    return get_and_parse(
        get_settings().routes.match_summary, Match, params={"match_id": match_id}, base_route=BaseRoute.site
    )


def get_scorecard(match_id) -> Scorecard:
    match = get_match(match_id)
    return Scorecard(match=match)


def get_play_by_play(match_id: int, page: int = 1, innings: int = 1) -> list[CommentaryItem]:
    response = get_and_parse(
        get_settings().routes.play_by_play_page,
        APIResponseCommentary,
        {"match_id": match_id, "page": page, "innings": innings},
        True,
        BaseRoute.site,
    )
    return response.commentary.items if response and response.commentary else []
