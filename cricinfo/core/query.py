from cricinfo.config import get_settings
from cricinfo.source_models.player import Player

from .api_helper import get_and_parse


def get_player(player_id: int) -> Player:
    return get_and_parse(get_settings().routes.player, Player, params={"{player_id}": player_id})



