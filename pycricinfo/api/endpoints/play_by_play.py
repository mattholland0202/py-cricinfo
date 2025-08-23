from fastapi import APIRouter, Depends, Path, Query, status

from pycricinfo.cricinfo.call_cricinfo_api import get_play_by_play
from pycricinfo.source_models.api.commentary import CommentaryItem

router = APIRouter(prefix="", tags=["play_by_play"])


class PageAndInningsQueryParameters:
    def __init__(
        self,
        page: int | None = Query(1, description="Which page of data to return"),
        innings: int | None = Query(1, description="Which innings of the game to get data from"),
    ):
        self.page = page
        self.innings = innings


@router.get(
    "/match/{match_id}/play_by_play",
    responses={status.HTTP_200_OK: {"description": "The match summary"}},
    summary="Get a page of ball-by-ball data",
)
async def match_play_by_play(
    match_id: int = Path(description="The Match ID"), pi: PageAndInningsQueryParameters = Depends()
) -> list[CommentaryItem]:
    return get_play_by_play(match_id, pi.page, pi.innings)
