from enum import Enum, auto
from functools import lru_cache

from pydantic import BaseModel
from pydantic_settings import BaseSettings


class BaseRoute(Enum):
    core: str = auto()
    site: str = auto()
    page: str = auto()


class CoreAPIRoutes(BaseModel):
    team: str = "events/0/teams/{team_id}"
    team_players: str = "cricket/teams/{team_id}/athletes"
    player: str = "teams/0/athletes/{player_id}"
    match_basic: str = "events/{match_id}"
    match_team: str = "leagues/0/events/{match_id}/competitions/{match_id}/competitors/{team_id}"
    match_summary: str = "0/summary?event={match_id}"
    league: str = "leagues/{league_id}"
    play_by_play_page: str = "0/playbyplay?event={match_id}&page={page}&period={innings}"
    venue: str = "venues/{venue_id}"


class PageRoutes(BaseModel):
    series_in_season: str = "series/index.html?season={season_name};view=season"
    matches_in_series: str = "match/index/series.html?series={series_id}"


class PageHeaders(BaseModel):
    user_agent: str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:138.0) Gecko/20100101 Firefox/138.0"
    accept: str = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"


class Settings(BaseSettings):
    core_base_route_v2: str = "http://core.espnuk.org/v2/sports/cricket/"
    site_base_route_v2: str = "http://site.api.espn.com/apis/site/v2/sports/cricket/"
    pages_base_route: str = "https://www.espncricinfo.com/ci/engine/"

    routes: CoreAPIRoutes = CoreAPIRoutes()
    page_routes: PageRoutes = PageRoutes()
    page_headers: PageHeaders = PageHeaders()
    api_response_output_folder: str = "responses"

    match_classes: dict[int, str] = {
        1: "Test",
        2: "ODI",
        3: "T20I",
        4: "First Class",
        5: "List A",
        6: "T20",
        8: "Women's Test",
        9: "Women's ODI",
        10: "Women's T20I",
        11: "Combined Test, ODI and T20I",
        12: "Combined First Class, List A and T20",
        13: "All cricket, including minor cricket",
        20: "Under 19s Youth Test",
        21: "Under 19s Youth ODI",
        23: "Women's T20",
    }


@lru_cache
def get_settings():
    return Settings()
