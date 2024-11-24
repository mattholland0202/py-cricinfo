from cricinfo.source_models.common import Ref, CCBaseModel

class Team(CCBaseModel):
    id: str
    abbreviation: str
    display_name: str
    color: str
    logos: list[Ref]