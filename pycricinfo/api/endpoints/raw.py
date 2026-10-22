"""Endpoints which return responses direct from the Cricinfo API, without any parsing."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, status

from pycricinfo.api.utils import PageAndInningsQueryParameters
from pycricinfo.api_helper import get_request
from pycricinfo.config import BaseRoute, get_settings

router = APIRouter(prefix="/raw", tags=["Cricinfo: API"])


@router.get(
    "/match/{match_id}",
    responses={status.HTTP_200_OK: {"description": "The basic match data"}},
    summary="Get basic match data from the '/events' API",
    response_model=None,
)
async def match_basic(match_id: Annotated[int, Path(description="The Match ID")]) -> dict | str:
    """Get a match's basic data, as returned by the Core API's '/events' endpoint."""
    return await get_request(get_settings().routes.match_basic, params={"match_id": match_id})


@router.get(
    "/match/{match_id}/team/{team_id}",
    responses={status.HTTP_200_OK: {"description": "The basic match data"}},
    summary="Get a match's Team",
    response_model=None,
)
async def match_team(
    match_id: Annotated[int, Path(description="The Match ID")], team_id: Annotated[int, Path(description="The Team ID")]
) -> dict | str:
    """Get one of the Teams in a match, as returned by the Core API."""
    return await get_request(
        get_settings().routes.match_team,
        {"match_id": match_id, "team_id": team_id},
        BaseRoute.core,
    )


@router.get(
    "/match/{match_id}/team/{team_id}/roster",
    responses={status.HTTP_200_OK: {"description": "The basic match data"}},
    summary="Get a match Team's roster",
    response_model=None,
)
async def match_team_roster(
    match_id: Annotated[int, Path(description="The Match ID")], team_id: Annotated[int, Path(description="The Team ID")]
) -> dict | str:
    """Get a Team's roster for a match, as returned by the Core API."""
    return await get_request(
        get_settings().routes.match_team_roster,
        {"match_id": match_id, "team_id": team_id},
        BaseRoute.core,
    )


@router.get(
    "/match/{match_id}/team/{team_id}/innings",
    responses={status.HTTP_200_OK: {"description": "The basic match data"}},
    summary="Get a match Team's innings",
    response_model=None,
)
async def match_team_all_innings(
    match_id: Annotated[int, Path(description="The Match ID")],
    team_id: Annotated[int, Path(description="The Team ID")],
) -> dict | str:
    """Get all of a Team's innings in a match, as returned by the Core API."""
    return await get_request(
        get_settings().routes.match_team_all_innings,
        {"match_id": match_id, "team_id": team_id},
        BaseRoute.core,
    )


@router.get(
    "/match/{match_id}/team/{team_id}/innings/{innings}",
    responses={status.HTTP_200_OK: {"description": "The basic match data"}},
    summary="Get a match Team's innings",
    response_model=None,
)
async def match_team_innings(
    match_id: Annotated[int, Path(description="The Match ID")],
    team_id: Annotated[int, Path(description="The Team ID")],
    innings: Annotated[int, Path(description="The innings number")],
) -> dict | str:
    """Get one of a Team's innings in a match, as returned by the Core API."""
    return await get_request(
        get_settings().routes.match_team_innings,
        {"match_id": match_id, "team_id": team_id, "innings": innings},
        BaseRoute.core,
    )


@router.get(
    "/series/{series_id}/match/{match_id}/team/{team_id}/statistics",
    responses={status.HTTP_200_OK: {"description": "The basic match data"}},
    summary="Get a match Team's statistics",
    response_model=None,
)
async def match_team_statistics(
    series_id: Annotated[int, Path(description="The Series ID")],
    match_id: Annotated[int, Path(description="The Match ID")],
    team_id: Annotated[int, Path(description="The Team ID")],
) -> dict | str:
    """Get a Team's statistics for a match, as returned by the Core API."""
    return await get_request(
        get_settings().routes.match_team_statistics,
        {"series_id": series_id, "match_id": match_id, "team_id": team_id},
        BaseRoute.core,
    )


@router.get(
    "/match/{match_id}/team/{team_id}/player/{player_id}/innings",
    responses={status.HTTP_200_OK: {"description": "The basic match data"}},
    summary="Get a match Team's innings",
    response_model=None,
)
async def match_player_all_innings(
    match_id: Annotated[int, Path(description="The Match ID")],
    team_id: Annotated[int, Path(description="The Team ID")],
    player_id: Annotated[int, Path(description="The Player ID")],
) -> dict | str:
    """Get all of a Player's innings in a match, as returned by the Core API."""
    return await get_request(
        get_settings().routes.match_player_all_innings,
        {"match_id": match_id, "team_id": team_id, "player_id": player_id},
        BaseRoute.core,
    )


@router.get(
    "/series/{series_id}/match/{match_id}/team/{team_id}/player/{player_id}/innings/{innings}/statistics",
    responses={status.HTTP_200_OK: {"description": "The basic match data"}},
    summary="Get statistics for a player's innings",
    response_model=None,
)
async def match_player_innings_statistics(
    series_id: Annotated[int, Path(description="The Series ID")],
    match_id: Annotated[int, Path(description="The Match ID")],
    team_id: Annotated[int, Path(description="The Team ID")],
    player_id: Annotated[int, Path(description="The Player ID")],
    innings: Annotated[int, Path(description="The innings number")],
) -> dict | str:
    """Get the statistics for one of a Player's innings in a match, as returned by the Core API."""
    return await get_request(
        get_settings().routes.match_player_innings_statistics,
        {
            "series_id": series_id,
            "match_id": match_id,
            "team_id": team_id,
            "player_id": player_id,
            "innings": innings,
        },
        BaseRoute.core,
    )


@router.get(
    "/match/{match_id}/play_by_play_page",
    responses={status.HTTP_200_OK: {"description": "The match summary"}},
    summary="Get a page of ball-by-ball data",
    response_model=None,
)
async def match_play_by_play(
    match_id: Annotated[int, Path(description="The Match ID")], pi: Annotated[PageAndInningsQueryParameters, Depends()]
) -> dict | str:
    """Get a page of ball-by-ball commentary for an innings, as returned by the Site API."""
    return await get_request(
        get_settings().routes.play_by_play_page,
        {"match_id": match_id, "page": pi.page, "innings": pi.innings},
        BaseRoute.site,
    )


@router.get(
    "/match_summary/{series_id}/{match_id}",
    responses={status.HTTP_200_OK: {"description": "The match summary"}},
    summary="Get a match summary",
    response_model=None,
)
async def match_summary(
    series_id: Annotated[int, Path(description="The Series ID")],
    match_id: Annotated[int, Path(description="The Match ID")],
) -> dict | str:
    """Get a match summary, as returned by the Site API."""
    return await get_request(
        get_settings().routes.match_summary,
        params={"series_id": series_id, "match_id": match_id},
        base_route=BaseRoute.site,
    )


@router.get(
    "/venue/{venue_id}",
    responses={status.HTTP_200_OK: {"description": "A Venue's data"}},
    summary="Get a Venue",
    response_model=None,
)
async def venue(venue_id: Annotated[int, Path(description="The Venue ID")]) -> dict | str:
    """Get a Venue, as returned by the Core API."""
    return await get_request(get_settings().routes.venue, params={"venue_id": venue_id})


@router.get(
    "/league/{league_id}",
    responses={status.HTTP_200_OK: {"description": "A League's data"}},
    summary="Get a League",
    response_model=None,
)
async def league(league_id: Annotated[int, Path(description="The League ID")]) -> dict | str:
    """Get a League, as returned by the Core API."""
    return await get_request(get_settings().routes.league, params={"league_id": league_id})


@router.get(
    "/league/{league_id}/event/{event_id}",
    responses={status.HTTP_200_OK: {"description": "A League's data"}},
    summary="Get an event (aka: a series of matches) in a League",
    response_model=None,
)
async def series_in_league(
    league_id: Annotated[int, Path(description="The League ID")],
    event_id: Annotated[int, Path(description="The Event ID")],
) -> dict | str:
    """Get an event (a series of matches) in a League, as returned by the Core API."""
    return await get_request(get_settings().routes.league_event, params={"league_id": league_id, "event_id": event_id})


@router.get(
    "/team/{team_id}",
    responses={status.HTTP_200_OK: {"description": "The Team data"}},
    summary="Get Team data",
    response_model=None,
)
async def team(team_id: Annotated[int, Path(description="The Team ID")]) -> dict | str:
    """Get a Team, as returned by the Core API."""
    return await get_request(get_settings().routes.team, params={"team_id": team_id})


@router.get(
    "/player/{player_id}",
    responses={status.HTTP_200_OK: {"description": "The Player"}},
    summary="Get Player",
    response_model=None,
)
async def player(player_id: Annotated[int, Path(description="The Player ID")]) -> dict | str:
    """Get a Player, as returned by the Core API."""
    return await get_request(get_settings().routes.player, params={"player_id": player_id})
