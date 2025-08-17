from pycricinfo.config import BaseRoute, get_settings
from pycricinfo.cricinfo.api_helper import get_and_parse, get_request
from pycricinfo.output_models.scorecard import CricinfoScorecard
from pycricinfo.source_models.api.commentary import APIResponseCommentary, CommentaryItem
from pycricinfo.source_models.api.match import Match
from pycricinfo.source_models.api.match_basic import MatchBasic
from pycricinfo.source_models.api.player import Player
from pycricinfo.source_models.api.team import TeamFull


def get_player(player_id: int) -> Player:
    """
    Get a player by their ID.

    Parameters
    ----------
    player_id : int
        The ID of the player to retrieve.

    Returns
    -------
    Player
        A parsed Pydantic model representing the player.
    """
    return get_and_parse(get_settings().routes.player, Player, params={"player_id": player_id})


def get_team(team_id: int) -> TeamFull:
    """
    Get a team by its ID.

    Parameters
    ----------
    team_id : int
        The ID of the team to retrieve.

    Returns
    -------
    TeamFull
        A parsed Pydantic model representing the team.
    """
    # TODO: Format "classes" field onto what match type they represent
    return get_and_parse(get_settings().routes.team, TeamFull, params={"team_id": team_id})


def get_match_basic(match_id: int) -> MatchBasic:
    """
    Get basic match information by match ID.

    Parameters
    ----------
    match_id : int
        The ID of the match to retrieve.

    Returns
    -------
    MatchBasic
        A parsed Pydantic model representing the basic match information.
    """
    return get_and_parse(get_settings().routes.match_basic, MatchBasic, params={"match_id": match_id})


def get_match(series_id: int, match_id: int) -> Match:
    """
    Get detailed match information by match ID.

    Parameters
    ----------
    series_id : int
        The ID of the series to which the match belongs.

    match_id : int
        The ID of the match to retrieve.

    Returns
    -------
    Match
        A parsed Pydantic model representing the match details.
    """
    return get_and_parse(
        get_settings().routes.match_summary,
        Match,
        params={"series_id": series_id, "match_id": match_id},
        base_route=BaseRoute.site,
    )


def get_match_raw(series_id: int, match_id: int) -> dict:
    """
    Get raw match data by match ID.

    Parameters
    ----------
    series_id : int
        The ID of the series to which the match belongs.

    match_id : int
        The ID of the match to retrieve.

    Returns
    -------
    dict
        The raw match data as a dictionary.
    """
    return get_request(
        get_settings().routes.match_summary,
        params={"series_id": series_id, "match_id": match_id},
        base_route=BaseRoute.site,
        response_output_sub_folder="matches",
    )


def get_scorecard(series_id: int, match_id: int) -> CricinfoScorecard:
    """
    Get a match and generate and return a scorecard for it.

    Parameters
    ----------
    match_id : int
        The ID of the match for which to generate the scorecard.

    Returns
    -------
    Scorecard
        A scorecard object containing match details and scores.
    """
    match = get_match(series_id, match_id)
    return CricinfoScorecard(match=match)


def get_play_by_play(match_id: int, page: int = 1, innings: int = 1) -> list[CommentaryItem]:
    """
    Get a page of ball-by-ball data for a match.

    Parameters
    ----------
    match_id : int
        The ID of the match for which to retrieve ball-by-ball commentary.
    page : int, optional
        The page of commentary to return, by default 1
    innings : int, optional
        How many items the page should contain, by default 1

    Returns
    -------
    list[CommentaryItem]
        A list of parsed Pydantic models representing the ball-by-ball commentary.
    """
    response = get_and_parse(
        get_settings().routes.play_by_play_page,
        APIResponseCommentary,
        {"match_id": match_id, "page": page, "innings": innings},
        True,
        BaseRoute.site,
    )
    return response.commentary.items if response and response.commentary else []
