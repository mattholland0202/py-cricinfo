from fastapi import APIRouter, Path, status

from pycricinfo.call_cricinfo_api import get_player
from pycricinfo.models.source.api.player import Player
from pycricinfo.models.source.pages.player import Career
from pycricinfo.player_stats_pages import get_player_career_stats_from_stats_pages

router = APIRouter(prefix="/player", tags=["player"])


@router.get("/{player_id}", responses={status.HTTP_200_OK: {"description": "The Player"}}, summary="Get Player")
async def player(player_id: int = Path(description="The Player ID")) -> Player:
    return await get_player(player_id)


@router.get(
    "/{player_id}/career",
    responses={status.HTTP_200_OK: {"description": "The Player career stats"}},
    summary="Get Player career stats",
)
async def player_career(player_id: int = Path(description="The Player ID")) -> Career:
    return await get_player_career_stats_from_stats_pages(player_id=player_id)
