import requests
from fastapi import APIRouter, Path, status

from pycricinfo.cricinfo.call_cricinfo_api import get_match, get_match_basic
from pycricinfo.source_models.api.match import Match
from pycricinfo.source_models.api.match_basic import MatchBasic

router = APIRouter(prefix="/match", tags=["match"])


@router.get(
    "/{match_id}",
    responses={status.HTTP_200_OK: {"description": "The basic match data"}},
    summary="Get basic match data from the '/events' API",
)
async def match_basic(match_id: int = Path(description="The Match ID")) -> MatchBasic:
    return get_match_basic(match_id)


@router.get(
    "/{match_id}/team/{team_id}",
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
    "/summary/{series_id}/{match_id}",
    responses={status.HTTP_200_OK: {"description": "The match summary"}},
    summary="Get a match summary",
)
async def match(
    series_id: int = Path(description="The Series ID"), match_id: int = Path(description="The Match ID")
) -> Match:
    return get_match(series_id, match_id)
