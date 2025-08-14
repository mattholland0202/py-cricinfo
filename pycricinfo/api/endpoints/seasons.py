from typing import Literal

from fastapi import APIRouter, Path, Query, status

from pycricinfo.search.seasons import get_match_types_in_season
from pycricinfo.search.series import extract_match_ids_from_series
from pycricinfo.source_models.pages.series import MatchResult, MatchType

router = APIRouter(prefix="/matches", tags=["matches"])


@router.get(
    "/season/{season_name}",
    responses={
        status.HTTP_200_OK: {
            "description": "A list of match types, each containing a list of series in that match type for this season"
        }
    },
    summary="Get a list of match types, each containing a list of series in that match type for this season",
)
async def match_types_in_season(
    season_name: int = Path(description='The name of the season to get matches for, e.g. "2024" or "2020-21"'),
    match_type_name: Literal[
        "Tests",
        "One-Day Internationals",
        "Twenty20 Internationals",
        "First-class",
        "List A",
        "Twenty20",
        "Women's One-Day Internationals",
        "Women's Twenty20 Internationals",
        "Youth Tests",
        "Youth One-Day Internationals",
        "Women's Twenty20",
        "Tour",
        "Minor tour",
        "Other matches",
        "Other one-day/limited-overs matches",
        "Other Twenty20 matches",
    ] = Query(default=None, description="Filter the response to just matches of the named type"),
) -> list[MatchType]:
    match_types = get_match_types_in_season(season_name)

    if match_type_name:
        match_types = [m for m in match_types if m.name.lower() == match_type_name.lower()]

    return match_types


@router.get(
    "/series/{data_series_id}",
    responses={status.HTTP_200_OK: {"description": "A list of IDs of the matches in the supplied series"}},
    summary="Get a list of IDs of the matches in the supplied series",
)
async def match_ids_in_series(data_series_id: int = Path(description="The ID of a series")) -> list[MatchResult]:
    return extract_match_ids_from_series(data_series_id)
