"""Endpoints for searching seasons and series."""

from typing import Annotated, Optional

from fastapi import APIRouter, Path, Query, status

from pycricinfo.models.source.pages.series import MatchResult, MatchTypeWithSeries
from pycricinfo.search.seasons import get_match_types_in_season
from pycricinfo.search.series import get_match_results_in_series
from pycricinfo.types.match_types import MatchTypeNames

router = APIRouter(prefix="", tags=["seasons"])


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
    season_name: Annotated[
        int | str, Path(description='The name of the season to get matches for, e.g. "2024" or "2020-21"')
    ],
    match_type_name: Annotated[
        Optional[MatchTypeNames], Query(description="Filter the response to just matches of the named type")
    ] = None,
) -> list[MatchTypeWithSeries]:
    """Get the series in a season, grouped by match type."""
    season_name = season_name.replace("-", "/") if isinstance(season_name, str) else season_name
    return await get_match_types_in_season(season_name, match_type_name)


@router.get(
    "/series/{data_series_id}",
    responses={status.HTTP_200_OK: {"description": "A list of IDs of the matches in the supplied series"}},
    summary="Get a list of IDs of the matches in the supplied series",
)
async def match_ids_in_series(
    data_series_id: Annotated[int, Path(description="The ID of a series")],
) -> list[MatchResult]:
    """Get the matches in a series, with their scores and results."""
    return await get_match_results_in_series(data_series_id)
