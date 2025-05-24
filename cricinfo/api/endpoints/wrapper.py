import requests
from fastapi import APIRouter, Depends, Path, Query, status

from cricinfo.output_models.scorecard import Scorecard
from cricinfo.source_models.commentary import APIResponseCommentary
from cricinfo.source_models.match import Match
from cricinfo.source_models.player import Player
from cricinfo.utils import load_dict_to_model
from cricinfo.core.query import get_player

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
async def get_team(team_id: int = Path(description="The Team ID")):
    response = requests.get(f"http://core.espnuk.org/v2/sports/cricket/events/0/teams/{team_id}").json()
    return response


@router.get(
    "/team/{team_id}/players",
    responses={status.HTTP_200_OK: {"description": "The Team's players"}},
    summary="Get Team Players",
)
async def team_players(team_id: int = Path(description="The Team ID")):
    response = requests.get(f"http://core.espnuk.org/v2/sports/cricket/teams/{team_id}/athletes").json()
    return response


@router.get("/player/{player_id}", responses={status.HTTP_200_OK: {"description": "The Player"}}, summary="Get Player")
async def player(player_id: int = Path(description="The Player ID")) -> Player:
    return get_player(player_id)


@router.get(
    "/match/{match_id}/basic",
    responses={status.HTTP_200_OK: {"description": "The basic match data"}},
    summary="Get basic match data from the '/events' API",
)
async def get_match_basic(match_id: int = Path(description="The Match ID")):
    response = requests.get(f"http://core.espnuk.org/v2/sports/cricket/events/{match_id}").json()
    return response


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
async def get_match_summary(match_id: int = Path(description="The Match ID")):
    response = requests.get(f"http://site.api.espn.com/apis/site/v2/sports/cricket/0/summary?event={match_id}").json()
    model = Match.model_validate(response)
    sc = Scorecard(match=model)
    return sc


@router.get(
    "/match/{match_id}/play_by_play",
    responses={status.HTTP_200_OK: {"description": "The match summary"}},
    summary="Get a page of ball-by-ball data",
)
async def get_match_play_by_play(
    match_id: int = Path(description="The Match ID"), pi: PageAndInningsQueryParameters = Depends()
):
    response = requests.get(
        f"http://site.api.espn.com/apis/site/v2/sports/cricket/0/playbyplay?event={match_id}&page={pi.page}&period={pi.innings}"
    ).json()
    model = load_dict_to_model(response, APIResponseCommentary)
    return [
        f"{item.over.overs}: {item.short_text} - {item.current_innings_score.score}" for item in model.commentary.items
    ]
