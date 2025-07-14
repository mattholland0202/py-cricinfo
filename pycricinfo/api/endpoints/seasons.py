from fastapi import APIRouter, Path, status

from pycricinfo.search.seasons import get_matches_in_season
from pycricinfo.source_models.pages.series import MatchType

router = APIRouter(prefix="/seasons", tags=["seasons"])


@router.get(
    "/{season_name}",
    responses={
        status.HTTP_200_OK: {
            "description": "A list of match types, each containing a list of series in that match type for this season"
        }
    },
    summary="Get a list of match types, each containing a list of series in that match type for this season",
)
async def matches(
    season_name: int = Path(description='The name of the season to get matches for, e.g. "2024" or "2020-21"'),
) -> list[MatchType]:
    return get_matches_in_season(season_name)
