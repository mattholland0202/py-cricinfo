from fastapi import APIRouter, Path, Query, status

from pycricinfo.config import MatchTypeNames
from pycricinfo.search.seasons import get_match_types_in_season
from pycricinfo.search.series import extract_match_ids_from_series
from pycricinfo.source_models.pages.series import MatchResult, MatchType

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
    season_name: int | str = Path(description='The name of the season to get matches for, e.g. "2024" or "2020-21"'),
    match_type_name: MatchTypeNames = Query(
        default=None, description="Filter the response to just matches of the named type"
    ),
) -> list[MatchType]:
    season_name = season_name.replace("-", "/") if isinstance(season_name, str) else season_name
    match_types = get_match_types_in_season(season_name, match_type_name)

    return match_types


@router.get(
    "/series/{data_series_id}",
    responses={status.HTTP_200_OK: {"description": "A list of IDs of the matches in the supplied series"}},
    summary="Get a list of IDs of the matches in the supplied series",
)
async def match_ids_in_series(data_series_id: int = Path(description="The ID of a series")) -> list[MatchResult]:
    return extract_match_ids_from_series(data_series_id)
