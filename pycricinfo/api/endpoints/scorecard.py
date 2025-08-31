from fastapi import APIRouter, Path, status

from pycricinfo.cricinfo.call_cricinfo_api import (
    get_scorecard,
)
from pycricinfo.output_models.scorecard import CricinfoScorecard

router = APIRouter(prefix="/scorecard", tags=["scorecard"])


@router.get(
    "/{series_id}/{match_id}",
    responses={status.HTTP_200_OK: {"description": "The match scorecard"}},
    summary="Get a match scorecard",
)
async def scorecard(
    series_id: int = Path(description="The Series ID"), match_id: int = Path(description="The Match ID")
) -> CricinfoScorecard:
    return get_scorecard(series_id, match_id)
