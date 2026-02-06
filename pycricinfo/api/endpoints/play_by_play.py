from typing import Annotated

from fastapi import APIRouter, Depends, Path, status

from pycricinfo.api.utils import PageAndInningsQueryParameters
from pycricinfo.call_cricinfo_api import get_play_by_play
from pycricinfo.models.source.api.commentary import Commentary

router = APIRouter(prefix="", tags=["play_by_play"])


@router.get(
    "/match/{match_id}/play_by_play",
    responses={status.HTTP_200_OK: {"description": "The match summary"}},
    summary="Get a page of ball-by-ball data",
)
async def match_play_by_play_api(
    match_id: Annotated[int, Path(description="The Match ID")], pi: PageAndInningsQueryParameters = Depends()
) -> Commentary:
    return await get_play_by_play(match_id, pi.innings, pi.page)
