import requests
from fastapi import APIRouter, Depends, Path, Query, status

from pycricinfo.core.query import get_match_basic, get_play_by_play, get_player, get_scorecard, get_team
from pycricinfo.output_models.scorecard import Scorecard
from pycricinfo.source_models.commentary import CommentaryItem
from pycricinfo.source_models.match import MatchBasic
from pycricinfo.source_models.player import Player
from pycricinfo.source_models.team import TeamFull

router = APIRouter(prefix="/wrapper", tags=["wrapper"])


class PageAndInningsQueryParameters:
    def __init__(
        self,
        page: int | None = Query(1, description="Which page of data to return"),
        innings: int | None = Query(1, description="Which innings of the game to get data from"),
    ):
        self.page = page
        self.innings = innings


@router.get(
    "/team/{team_id}", responses={status.HTTP_200_OK: {"description": "The Team data"}}, summary="Get Team data"
)
async def team(team_id: int = Path(description="The Team ID")) -> TeamFull:
    return get_team(team_id)


@router.get("/player/{player_id}", responses={status.HTTP_200_OK: {"description": "The Player"}}, summary="Get Player")
async def player(player_id: int = Path(description="The Player ID")) -> Player:
    return get_player(player_id)


@router.get(
    "/match/{match_id}/basic",
    responses={status.HTTP_200_OK: {"description": "The basic match data"}},
    summary="Get basic match data from the '/events' API",
)
async def match_basic(match_id: int = Path(description="The Match ID")) -> MatchBasic:
    return get_match_basic(match_id)


@router.get(
    "/match/{match_id}/team/{team_id}",
    responses={status.HTTP_200_OK: {"description": "The basic match data"}},
    summary="Get a match's Team",
)
async def get_match_team(
    match_id: int = Path(description="The Match ID"), team_id: int = Path(description="The Team ID")
):
    response = requests.get(
        f"http://core.espnuk.org/v2/sports/cricket/leagues/0/events/{match_id}/competitions/{match_id}/competitors/{team_id}"
    ).json()
    return response


@router.get(
    "/match/{match_id}/summary",
    responses={status.HTTP_200_OK: {"description": "The match summary"}},
    summary="Get a match summary",
)
async def scorecard(match_id: int = Path(description="The Match ID")) -> Scorecard:
    return get_scorecard(match_id)


@router.get(
    "/match/{match_id}/play_by_play",
    responses={status.HTTP_200_OK: {"description": "The match summary"}},
    summary="Get a page of ball-by-ball data",
)
async def match_play_by_play(
    match_id: int = Path(description="The Match ID"), pi: PageAndInningsQueryParameters = Depends()
) -> list[CommentaryItem]:
    return get_play_by_play(match_id, pi.page, pi.innings)
