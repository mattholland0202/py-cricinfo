from typing import Optional

import aiohttp

from pycricinfo.api_helper import get_and_parse, get_request
from pycricinfo.config import BaseRoute, get_settings
from pycricinfo.models.output.scorecard import CricinfoScorecard
from pycricinfo.models.source import APIResponseCommentary, Commentary, Match, MatchBasic, Player, TeamFull


async def get_player(player_id: int, session: Optional[aiohttp.ClientSession] = None) -> Player:
    """
    Get a player by their ID.

    Parameters
    ----------
    player_id : int
        The ID of the player to retrieve.
    session : aiohttp.ClientSession, optional
        An existing session to use for the request, by default None

    Returns
    -------
    Player
        A parsed Pydantic model representing the player.
    """
    return await get_and_parse(get_settings().routes.player, Player, params={"player_id": player_id}, session=session)


async def get_team(team_id: int, session: Optional[aiohttp.ClientSession] = None) -> TeamFull:
    """
    Get a team by its ID.

    Parameters
    ----------
    team_id : int
        The ID of the team to retrieve.
    session : aiohttp.ClientSession, optional
        An existing session to use for the request, by default None

    Returns
    -------
    TeamFull
        A parsed Pydantic model representing the team.
    """
    return await get_and_parse(get_settings().routes.team, TeamFull, params={"team_id": team_id}, session=session)


async def get_match_basic(match_id: int, session: Optional[aiohttp.ClientSession] = None) -> MatchBasic:
    """
    Get basic match information by match ID.

    Parameters
    ----------
    match_id : int
        The ID of the match to retrieve.
    session : aiohttp.ClientSession, optional
        An existing session to use for the request, by default None

    Returns
    -------
    MatchBasic
        A parsed Pydantic model representing the basic match information.
    """
    return await get_and_parse(
        get_settings().routes.match_basic, MatchBasic, params={"match_id": match_id}, session=session
    )


async def get_match(series_id: int, match_id: int, session: Optional[aiohttp.ClientSession] = None) -> Match:
    """
    Get detailed match information by match ID.

    Parameters
    ----------
    series_id : int
        The ID of the series to which the match belongs.
    match_id : int
        The ID of the match to retrieve.
    session : aiohttp.ClientSession, optional
        An existing session to use for the request, by default None

    Returns
    -------
    Match
        A parsed Pydantic model representing the match details.
    """
    return await get_and_parse(
        get_settings().routes.match_summary,
        Match,
        params={"series_id": series_id, "match_id": match_id},
        base_route=BaseRoute.site,
        session=session,
    )


async def get_match_raw(series_id: int, match_id: int, session: Optional[aiohttp.ClientSession] = None) -> dict:
    """
    Get raw match data by match ID.

    Parameters
    ----------
    series_id : int
        The ID of the series to which the match belongs.
    match_id : int
        The ID of the match to retrieve.
    session : aiohttp.ClientSession, optional
        An existing session to use for the request, by default None

    Returns
    -------
    dict
        The raw match data as a dictionary.
    """
    return await get_request(
        get_settings().routes.match_summary,
        params={"series_id": series_id, "match_id": match_id},
        base_route=BaseRoute.site,
        response_output_sub_folder="matches",
        session=session,
    )


async def get_scorecard(
    series_id: int, match_id: int, session: Optional[aiohttp.ClientSession] = None
) -> CricinfoScorecard:
    """
    Get a match and generate and return a scorecard for it.

    Parameters
    ----------
    series_id : int
        The ID of the series to which the match belongs.
    match_id : int
        The ID of the match for which to generate the scorecard.
    session : aiohttp.ClientSession, optional
        An existing session to use for the request, by default None

    Returns
    -------
    Scorecard
        A scorecard object containing match details and scores.
    """
    match = await get_match(series_id, match_id, session=session)
    return CricinfoScorecard(match=match)


async def get_play_by_play(
    match_id: int, innings: int = 1, page: int = 1, session: Optional[aiohttp.ClientSession] = None
) -> Commentary:
    """
    Get a page of ball-by-ball data for a match, processed into a list of CommentaryItems.

    Parameters
    ----------
    match_id : int
        The ID of the match for which to retrieve ball-by-ball commentary.
    innings : int, optional
        Which innings to retrieve commentary for, by default 1
    page : int, optional
        The page of commentary to return, by default 1
    session : aiohttp.ClientSession, optional
        An existing session to use for the request, by default None

    Returns
    -------
    list[CommentaryItem]
        A list of parsed Pydantic models representing the ball-by-ball commentary.
    """
    response = await get_and_parse(
        get_settings().routes.play_by_play_page,
        APIResponseCommentary,
        {"match_id": match_id, "page": page, "innings": innings},
        True,
        BaseRoute.site,
        session=session,
    )
    return response.commentary if response and response.commentary else []


async def get_play_by_play_raw(
    match_id: int, page: int = 1, innings: int = 1, session: Optional[aiohttp.ClientSession] = None
) -> dict:
    """
    Get a page of ball-by-ball data for a match.

    Parameters
    ----------
    match_id : int
        The ID of the match for which to retrieve ball-by-ball commentary.
    page : int, optional
        The page of commentary to return, by default 1
    innings : int, optional
        Which innings to retrieve commentary for, by default 1
    session : aiohttp.ClientSession, optional
        An existing session to use for the request, by default None

    Returns
    -------
    dict
        The raw play-by-play data as a dictionary.
    """
    return await get_request(
        get_settings().routes.play_by_play_page,
        {"match_id": match_id, "page": page, "innings": innings},
        base_route=BaseRoute.site,
        response_output_sub_folder="play_by_play",
        session=session,
    )
