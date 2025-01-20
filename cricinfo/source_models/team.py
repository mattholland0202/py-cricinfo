from abc import ABC

from cricinfo.source_models.common import CCBaseModel, NameMixin, RefMixin


class TeamCommon(CCBaseModel, ABC):
    id: str
    abbreviation: str
    display_name: str

class TeamWithName(TeamCommon, NameMixin): ...

class TeamWithColorAndLogos(TeamCommon):
    color: str
    logos: list[RefMixin]