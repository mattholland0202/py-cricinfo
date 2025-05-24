from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

import os

DOTENV = os.path.join(os.path.dirname(__file__), "../.env")


def _load_version() -> str:
    base_path = Path(__file__).parent.parent
    file_path = (base_path / "version.txt").resolve()
    with open(file_path, "r") as file:
        version = file.readline()
    return version


class APIRoutes(BaseModel):
    team: str = "events/0/teams/{team_id}"
    team_players: str = "cricket/teams/{team_id}/athletes"
    player: str = "teams/0/athletes/{player_id}"
    match: str = "events/{match_id}"
    match_team: str = "leagues/0/events/{match_id}/competitions/{match_id}/competitors/{team_id}"
    match_summary: str = "0/summary?event={match_id}"
    play_by_play_page: str = "0/playbyplay?event={match_id}&page={page}&period={innings}"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=DOTENV, env_nested_delimiter="__", extra="allow")

    base_route_v2: str = "http://core.espnuk.org/v2/sports/cricket/"
    routes: APIRoutes = APIRoutes()
    version: str = _load_version()
    api_response_output_folder: str = "responses"


@lru_cache
def get_settings():
    return Settings()
