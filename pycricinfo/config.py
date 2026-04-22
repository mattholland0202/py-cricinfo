from enum import Enum, auto
from functools import lru_cache

from pydantic import BaseModel
from pydantic_settings import BaseSettings


class BaseRoute(Enum):
    core: str = auto()
    site: str = auto()
    page: str = auto()


class CoreAPIRoutes(BaseModel):
    team: str = "teams/{team_id}"
    team_players: str = "cricket/teams/{team_id}/athletes"
    player: str = "teams/0/athletes/{player_id}"
    match_basic: str = "events/{match_id}"
    match_team: str = "leagues/0/events/{match_id}/competitions/{match_id}/competitors/{team_id}"
    match_team_roster: str = "leagues/0/events/{match_id}/competitions/{match_id}/competitors/{team_id}/roster"
    match_team_all_innings: str = "leagues/0/events/{match_id}/competitions/{match_id}/competitors/{team_id}/linescores"
    match_team_innings: str = (
        "leagues/0/events/{match_id}/competitions/{match_id}/competitors/{team_id}/linescores/0/{innings}"
    )
    match_team_statistics: str = (
        "leagues/{series_id}/events/{match_id}/competitions/{match_id}/competitors/{team_id}/statistics"
    )
    match_player_all_innings: str = (
        "leagues/0/events/{match_id}/competitions/{match_id}/competitors/{team_id}/roster/{player_id}/linescores"
    )
    match_player_innings_statistics: str = (
        "leagues/{series_id}/events/{match_id}/competitions/{match_id}/competitors/{team_id}/"
        "roster/{player_id}/linescores/0/{innings}/statistics/0"
    )
    match_summary: str = "{series_id}/summary?event={match_id}"
    league: str = "leagues/{league_id}"
    league_event: str = "leagues/{league_id}/events/{event_id}"
    play_by_play_page: str = "0/playbyplay?event={match_id}&page={page}&period={innings}"
    venue: str = "venues/{venue_id}"


class PageRoutes(BaseModel):
    series_in_season: str = "series/index.html?season={season_name};view=season"
    matches_in_series: str = "match/index/series.html?series={series_id}"


class PageHeaders(BaseModel):
    user_agent: str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:148.0) Gecko/20100101 Firefox/148.0"
    accept: str = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"


class Settings(BaseSettings):
    core_base_route_v2: str = "http://core.espnuk.org/v2/sports/cricket/"
    site_base_route_v2: str = "http://site.api.espn.com/apis/site/v2/sports/cricket/"
    pages_base_route: str = "https://www.espncricinfo.com/ci/engine/"

    routes: CoreAPIRoutes = CoreAPIRoutes()
    page_routes: PageRoutes = PageRoutes()
    page_headers: PageHeaders = PageHeaders()
    api_response_output_folder: str = "responses"
    port: int = 8004

    # TODO: Combine with MatchTypeNames enum
    # 11, 12 and 13 have different meanings in API "match_class" and the records/StatsGuru section
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
        11: "Combined Test, ODI and T20I",  # aka: Other Matches (multi-day)
        12: "Combined First Class, List A and T20",  # aka: Other one-day/limited-overs matches
        13: "All cricket, including minor cricket",  # aka: Other Twenty20 matches
        14: "Youth Test",  # matches will have generalId: 11
        15: "Youth ODI",  # matches will have generalId: 12
        17: "Women's T20",
        20: "Under 19s Youth Test",
        21: "Under 19s Youth ODI",
        23: "Women's T20",
    }


@lru_cache
def get_settings():
    return Settings()
