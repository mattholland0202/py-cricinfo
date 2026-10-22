"""Endpoints for matches."""

from typing import Annotated

from fastapi import APIRouter, Path, status

from pycricinfo.call_cricinfo_api import get_match, get_match_basic, get_match_team
from pycricinfo.models.source.api.match import Match, MatchBasic, MatchCompetitorBasic

router = APIRouter(prefix="/match", tags=["match"])


@router.get(
    "/{match_id}",
    responses={status.HTTP_200_OK: {"description": "The basic match data"}},
    summary="Get basic match data from the '/events' API",
)
async def match_basic(match_id: Annotated[int, Path(description="The ID of the Match")]) -> MatchBasic:
    """Get a match's basic data, parsed from the Core API's '/events' endpoint."""
    return await get_match_basic(match_id)


@router.get(
    "/{match_id}/team/{team_id}",
    responses={status.HTTP_200_OK: {"description": "A team from a Match"}},
    summary="Get a match's Team",
)
async def match_team(
    match_id: Annotated[int, Path(description="The ID of the Match")],
    team_id: Annotated[int, Path(description="The ID of the Team")],
) -> MatchCompetitorBasic:
    """Get one of the Teams in a match, with links to its score, roster, innings and statistics."""
    return await get_match_team(match_id, team_id)


@router.get(
    "/summary/{series_id}/{match_id}",
    responses={status.HTTP_200_OK: {"description": "The match summary"}},
    summary="Get a match summary",
)
async def match_api(
    series_id: Annotated[int, Path(description="The Series ID")],
    match_id: Annotated[int, Path(description="The Match ID")],
) -> Match:
    """Get a match's full details, parsed from the Site API's match summary."""
    return await get_match(series_id, match_id)
