from fastapi import APIRouter, Path, status

from pycricinfo.call_cricinfo_api import get_team
from pycricinfo.models.source.api.team import TeamFull

router = APIRouter(prefix="/team", tags=["team"])


@router.get("/{team_id}", responses={status.HTTP_200_OK: {"description": "The Team data"}}, summary="Get Team data")
def team(team_id: int = Path(description="The Team ID")) -> TeamFull:
    return get_team(team_id)
