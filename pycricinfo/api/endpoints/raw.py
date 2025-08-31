import requests
from fastapi import APIRouter, Depends, Path, Query, status

from pycricinfo.config import BaseRoute, get_settings
from pycricinfo.cricinfo.api_helper import get_request

router = APIRouter(prefix="/raw", tags=["Cricinfo: API"])


class PageAndInningsQueryParameters:
    def __init__(
        self,
        page: int | None = Query(1, description="Which page of data to return"),
        innings: int | None = Query(1, description="Which innings of the game to get data from"),
    ):
        self.page = page
        self.innings = innings


@router.get(
    "/team/{team_id}", responses={status.HTTP_200_OK: {"description": "The Team data"}}, summary="Get Team data"
)
async def team(team_id: int = Path(description="The Team ID")):
    return get_request(get_settings().routes.team, params={"team_id": team_id})


@router.get("/player/{player_id}", responses={status.HTTP_200_OK: {"description": "The Player"}}, summary="Get Player")
async def player(player_id: int = Path(description="The Player ID")):
    return get_request(get_settings().routes.player, params={"player_id": player_id})


@router.get(
    "/match/{match_id}",
    responses={status.HTTP_200_OK: {"description": "The basic match data"}},
    summary="Get basic match data from the '/events' API",
)
async def match_basic(match_id: int = Path(description="The Match ID")):
    return get_request(get_settings().routes.match_basic, params={"match_id": match_id})


@router.get(
    "/match/{match_id}/team/{team_id}",
    responses={status.HTTP_200_OK: {"description": "The basic match data"}},
    summary="Get a match's Team",
)
async def match_team(match_id: int = Path(description="The Match ID"), team_id: int = Path(description="The Team ID")):
    response = requests.get(
        f"http://core.espnuk.org/v2/sports/cricket/leagues/0/events/{match_id}/competitions/{match_id}/competitors/{team_id}"
    ).json()
    return response


@router.get(
    "/match/{match_id}/team/{team_id}/roster",
    responses={status.HTTP_200_OK: {"description": "The basic match data"}},
    summary="Get a match Team's roster",
)
async def match_team_roster(
    match_id: int = Path(description="The Match ID"), team_id: int = Path(description="The Team ID")
):
    response = requests.get(
        f"http://core.espnuk.org/v2/sports/cricket/leagues/0/events/{match_id}/competitions/{match_id}/competitors/{team_id}/roster"
    ).json()
    return response


@router.get(
    "/match/{match_id}/team/{team_id}/innings",
    responses={status.HTTP_200_OK: {"description": "The basic match data"}},
    summary="Get a match Team's innings",
)
async def match_team_all_innings(
    match_id: int = Path(description="The Match ID"),
    team_id: int = Path(description="The Team ID"),
):
    response = requests.get(
        f"http://core.espnuk.org/v2/sports/cricket/leagues/0/events/{match_id}/competitions/{match_id}/competitors/{team_id}/linescores"
    ).json()
    return response


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
    response = requests.get(
        f"http://core.espnuk.org/v2/sports/cricket/leagues/0/events/{match_id}/competitions/{match_id}/competitors/{team_id}/linescores/0/{innings}"
    ).json()
    return response


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
    response = requests.get(
        f"http://core.espnuk.org/v2/sports/cricket/leagues/{series_id}/events/{match_id}/competitions/{match_id}/competitors/{team_id}/statistics"
    ).json()
    return response


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
    response = requests.get(
        f"http://core.espnuk.org/v2/sports/cricket/leagues/0/events/{match_id}/competitions/{match_id}/competitors/{team_id}/roster/{player_id}/linescores"
    ).json()
    return response


@router.get(
    "/series/{series_id}/match/{match_id}/team/{team_id}/player/{player_id}/innings/{innings}/statistics",
    responses={status.HTTP_200_OK: {"description": "The basic match data"}},
    summary="Get a match Team's innings",
)
async def match_player_innings(
    series_id: int = Path(description="The Series ID"),
    match_id: int = Path(description="The Match ID"),
    team_id: int = Path(description="The Team ID"),
    player_id: int = Path(description="The Player ID"),
    innings: int = Path(description="The innings number"),
):
    response = requests.get(
        f"http://core.espnuk.org/v2/sports/cricket/leagues/{series_id}/events/{match_id}/competitions/{match_id}/competitors/{team_id}/roster/{player_id}/linescores/0/{innings}/statistics/0"
    ).json()
    return response


@router.get(
    "/match_summary/{match_id}",
    responses={status.HTTP_200_OK: {"description": "The match summary"}},
    summary="Get a match summary",
)
async def match_summary(match_id: int = Path(description="The Match ID")):
    return get_request(get_settings().routes.match_summary, params={"match_id": match_id}, base_route=BaseRoute.site)


@router.get(
    "/match/{match_id}/play_by_play_page",
    responses={status.HTTP_200_OK: {"description": "The match summary"}},
    summary="Get a page of ball-by-ball data",
)
async def match_play_by_play(
    match_id: int = Path(description="The Match ID"), pi: PageAndInningsQueryParameters = Depends()
):
    return get_request(
        get_settings().routes.play_by_play_page,
        {"match_id": match_id, "page": pi.page, "innings": pi.innings},
        BaseRoute.site,
    )


@router.get(
    "/venue/{venue_id}",
    responses={status.HTTP_200_OK: {"description": "A Venue's data"}},
    summary="Get a Venue",
)
async def venue(venue_id: int = Path(description="The Venue ID")):
    return get_request(get_settings().routes.venue, params={"venue_id": venue_id})


@router.get(
    "/league/{league_id}",
    responses={status.HTTP_200_OK: {"description": "A League's data"}},
    summary="Get a League",
)
async def league(league_id: int = Path(description="The League ID")):
    return get_request(get_settings().routes.league, params={"league_id": league_id})
