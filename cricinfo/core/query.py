from cricinfo.config import get_settings
from cricinfo.source_models.player import Player
from cricinfo.source_models.team import TeamFull

from .api_helper import get_and_parse


def get_player(player_id: int) -> Player:
    return get_and_parse(get_settings().routes.player, Player, params={"player_id": player_id})


def get_team(team_id: int) -> TeamFull:
    # TODO: Format "classes" field onto what match type they represent
    return get_and_parse(get_settings().routes.team, TeamFull, params={"team_id": team_id})
