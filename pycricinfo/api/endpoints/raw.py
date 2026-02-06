from fastapi import APIRouter, Depends, Path, status

from pycricinfo.api.utils import PageAndInningsQueryParameters
from pycricinfo.api_helper import get_request
from pycricinfo.config import BaseRoute, get_settings

router = APIRouter(prefix="/raw", tags=["Cricinfo: API"])


@router.get(
    "/match/{match_id}",
    responses={status.HTTP_200_OK: {"description": "The basic match data"}},
    summary="Get basic match data from the '/events' API",
)
async def match_basic(match_id: int = Path(description="The Match ID")):
    return await get_request(get_settings().routes.match_basic, params={"match_id": match_id})


@router.get(
    "/match/{match_id}/team/{team_id}",
    responses={status.HTTP_200_OK: {"description": "The basic match data"}},
    summary="Get a match's Team",
)
async def match_team(match_id: int = Path(description="The Match ID"), team_id: int = Path(description="The Team ID")):
    return await get_request(
        "leagues/0/events/{match_id}/competitions/{match_id}/competitors/{team_id}",
        {"match_id": match_id, "team_id": team_id},
        BaseRoute.core,
    )


@router.get(
    "/match/{match_id}/team/{team_id}/roster",
    responses={status.HTTP_200_OK: {"description": "The basic match data"}},
    summary="Get a match Team's roster",
)
async def match_team_roster(
    match_id: int = Path(description="The Match ID"), team_id: int = Path(description="The Team ID")
):
    return await get_request(
        "leagues/0/events/{match_id}/competitions/{match_id}/competitors/{team_id}/roster",
        {"match_id": match_id, "team_id": team_id},
        BaseRoute.core,
    )


@router.get(
    "/match/{match_id}/team/{team_id}/innings",
    responses={status.HTTP_200_OK: {"description": "The basic match data"}},
    summary="Get a match Team's innings",
)
async def match_team_all_innings(
    match_id: int = Path(description="The Match ID"),
    team_id: int = Path(description="The Team ID"),
):
    return await get_request(
        "leagues/0/events/{match_id}/competitions/{match_id}/competitors/{team_id}/linescores",
        {"match_id": match_id, "team_id": team_id},
        BaseRoute.core,
    )


@router.get(
    "/match/{match_id}/team/{team_id}/innings/{innings}",
    responses={status.HTTP_200_OK: {"description": "The basic match data"}},
    summary="Get a match Team's innings",
)
async def match_team_innings(
    match_id: int = Path(description="The Match ID"),
    team_id: int = Path(description="The Team ID"),
    innings: int = Path(description="The innings number"),
):
    return await get_request(
        "leagues/0/events/{match_id}/competitions/{match_id}/competitors/{team_id}/linescores/0/{innings}",
        {"match_id": match_id, "team_id": team_id, "innings": innings},
        BaseRoute.core,
    )


@router.get(
    "/match/{match_id}/team/{team_id}/player/{player_id}/innings",
    responses={status.HTTP_200_OK: {"description": "The basic match data"}},
    summary="Get a match Team's innings",
)
async def match_player_all_innings(
    match_id: int = Path(description="The Match ID"),
    team_id: int = Path(description="The Team ID"),
    player_id: int = Path(description="The Player ID"),
):
    return await get_request(
        "leagues/0/events/{match_id}/competitions/{match_id}/competitors/{team_id}/roster/{player_id}/linescores",
        {"match_id": match_id, "team_id": team_id, "player_id": player_id},
        BaseRoute.core,
    )


@router.get(
    "/match/{match_id}/play_by_play_page",
    responses={status.HTTP_200_OK: {"description": "The match summary"}},
    summary="Get a page of ball-by-ball data",
)
async def match_play_by_play(
    match_id: int = Path(description="The Match ID"), pi: PageAndInningsQueryParameters = Depends()
):
    return await get_request(
        get_settings().routes.play_by_play_page,
        {"match_id": match_id, "page": pi.page, "innings": pi.innings},
        BaseRoute.site,
    )


@router.get(
    "/match_summary/{match_id}",
    responses={status.HTTP_200_OK: {"description": "The match summary"}},
    summary="Get a match summary",
)
async def match_summary(match_id: int = Path(description="The Match ID")):
    return await get_request(
        get_settings().routes.match_summary, params={"match_id": match_id}, base_route=BaseRoute.site
    )


@router.get(
    "/series/{series_id}/match/{match_id}/team/{team_id}/statistics",
    responses={status.HTTP_200_OK: {"description": "The basic match data"}},
    summary="Get a match Team's statistics",
)
async def match_team_statistics(
    series_id: int = Path(description="The Series ID"),
    match_id: int = Path(description="The Match ID"),
    team_id: int = Path(description="The Team ID"),
):
    return await get_request(
        "leagues/{series_id}/events/{match_id}/competitions/{match_id}/competitors/{team_id}/statistics",
        {"series_id": series_id, "match_id": match_id, "team_id": team_id},
        BaseRoute.core,
    )


@router.get(
    "/series/{series_id}/match/{match_id}/team/{team_id}/player/{player_id}/innings/{innings}/statistics",
    responses={status.HTTP_200_OK: {"description": "The basic match data"}},
    summary="Get statistics for a player's innings",
)
async def match_player_innings(
    series_id: int = Path(description="The Series ID"),
    match_id: int = Path(description="The Match ID"),
    team_id: int = Path(description="The Team ID"),
    player_id: int = Path(description="The Player ID"),
    innings: int = Path(description="The innings number"),
):
    return await get_request(
        (
            "leagues/{series_id}/events/{match_id}/competitions/{match_id}/competitors/"
            "{team_id}/roster/{player_id}/linescores/0/{innings}/statistics/0"
        ),
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
    "/venue/{venue_id}",
    responses={status.HTTP_200_OK: {"description": "A Venue's data"}},
    summary="Get a Venue",
)
async def venue(venue_id: int = Path(description="The Venue ID")):
    return await get_request(get_settings().routes.venue, params={"venue_id": venue_id})


@router.get(
    "/league/{league_id}",
    responses={status.HTTP_200_OK: {"description": "A League's data"}},
    summary="Get a League",
)
async def league(league_id: int = Path(description="The League ID")):
    return await get_request(get_settings().routes.league, params={"league_id": league_id})


@router.get(
    "/league/{league_id}/event/{event_id}",
    responses={status.HTTP_200_OK: {"description": "A League's data"}},
    summary="Get an event (aka: a series of matches) in a League",
)
async def series_in_league(
    league_id: int = Path(description="The League ID"), event_id: int = Path(description="The Event ID")
):
    return await get_request(get_settings().routes.league_event, params={"league_id": league_id, "event_id": event_id})


@router.get(
    "/team/{team_id}", responses={status.HTTP_200_OK: {"description": "The Team data"}}, summary="Get Team data"
)
async def team(team_id: int = Path(description="The Team ID")):
    return await get_request(get_settings().routes.team, params={"team_id": team_id})


@router.get("/player/{player_id}", responses={status.HTTP_200_OK: {"description": "The Player"}}, summary="Get Player")
async def player(player_id: int = Path(description="The Player ID")):
    return await get_request(get_settings().routes.player, params={"player_id": player_id})
