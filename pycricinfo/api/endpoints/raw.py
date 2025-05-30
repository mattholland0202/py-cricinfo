import requests
from fastapi import APIRouter, Depends, Path, Query, status

from pycricinfo.config import BaseRoute, get_settings
from pycricinfo.core.api_helper import get_request

router = APIRouter(prefix="/raw", tags=["raw"])


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
    "/match/{match_id}/basic",
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
async def get_match_team(
    match_id: int = Path(description="The Match ID"), team_id: int = Path(description="The Team ID")
):
    response = requests.get(
        f"http://core.espnuk.org/v2/sports/cricket/leagues/0/events/{match_id}/competitions/{match_id}/competitors/{team_id}"
    ).json()
    return response


@router.get(
    "/match/{match_id}/summary",
    responses={status.HTTP_200_OK: {"description": "The match summary"}},
    summary="Get a match summary",
)
async def scorecard(match_id: int = Path(description="The Match ID")):
    return get_request(get_settings().routes.match_summary, params={"match_id": match_id}, base_route=BaseRoute.site)


@router.get(
    "/match/{match_id}/play_by_play",
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
    summary="Get a venue",
)
async def venue(venue_id: int = Path(description="The Venuw ID")):
    return get_request(get_settings().routes.venue, params={"match_id": venue_id})
