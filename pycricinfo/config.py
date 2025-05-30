from enum import Enum, auto
from functools import lru_cache

from pydantic import BaseModel
from pydantic_settings import BaseSettings


class BaseRoute(Enum):
    core: str = auto()
    site: str = auto()


class CoreAPIRoutes(BaseModel):
    team: str = "events/0/teams/{team_id}"
    team_players: str = "cricket/teams/{team_id}/athletes"
    player: str = "teams/0/athletes/{player_id}"
    match_basic: str = "events/{match_id}"
    match_team: str = "leagues/0/events/{match_id}/competitions/{match_id}/competitors/{team_id}"
    match_summary: str = "0/summary?event={match_id}"
    play_by_play_page: str = "0/playbyplay?event={match_id}&page={page}&period={innings}"
    venue: str = "venues/{venue_id}"


class Settings(BaseSettings):
    core_base_route_v2: str = "http://core.espnuk.org/v2/sports/cricket/"
    site_base_route_v2: str = "http://site.api.espn.com/apis/site/v2/sports/cricket/"
    routes: CoreAPIRoutes = CoreAPIRoutes()
    api_response_output_folder: str = "responses"


@lru_cache
def get_settings():
    return Settings()
