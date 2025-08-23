from fastapi import APIRouter, Path, status

from pycricinfo.cricinfo.call_cricinfo_api import get_player
from pycricinfo.source_models.api.player import Player

router = APIRouter(prefix="/player", tags=["player"])


@router.get("/{player_id}", responses={status.HTTP_200_OK: {"description": "The Player"}}, summary="Get Player")
async def player(player_id: int = Path(description="The Player ID")) -> Player:
    return get_player(player_id)
