from typing import Annotated

from fastapi import APIRouter, Path, status

from pycricinfo.api_helper import get_request
from pycricinfo.call_cricinfo_api import get_match, get_match_basic
from pycricinfo.config import BaseRoute, get_settings
from pycricinfo.models.source.api.match import Match
from pycricinfo.models.source.api.match_basic import MatchBasic

router = APIRouter(prefix="/match", tags=["match"])


@router.get(
    "/{match_id}",
    responses={status.HTTP_200_OK: {"description": "The basic match data"}},
    summary="Get basic match data from the '/events' API",
)
async def match_basic(match_id: int = Path(description="The Match ID")) -> MatchBasic:
    return await get_match_basic(match_id)


@router.get(
    "/{match_id}/team/{team_id}",
    responses={status.HTTP_200_OK: {"description": "The basic match data"}},
    summary="Get a match's Team",
)
async def get_match_team(
    match_id: int = Path(description="The Match ID"), team_id: int = Path(description="The Team ID")
):
    return await get_request(
        get_settings().routes.match_team,
        params={"match_id": match_id, "team_id": team_id},
        base_route=BaseRoute.core,
    )


@router.get(
    "/summary/{series_id}/{match_id}",
    responses={status.HTTP_200_OK: {"description": "The match summary"}},
    summary="Get a match summary",
)
async def match_api(
    series_id: Annotated[int, Path(description="The Series ID")],
    match_id: Annotated[int, Path(description="The Match ID")],
) -> Match:
    return await get_match(series_id, match_id)
