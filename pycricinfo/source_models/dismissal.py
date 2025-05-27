from typing import Optional

from pydantic import BaseModel

from pycricinfo.source_models.athelete import AthleteWithFirstAndLastName
from pycricinfo.source_models.common import CCBaseModel


class DismissalFielder(CCBaseModel):
    athlete: AthleteWithFirstAndLastName
    display_order: int
    is_keeper: int
    is_substitute: int


class DismissalDetailsInnings(BaseModel):
    wickets: int
    runs: int


class DismissalDetailsOver(BaseModel):
    overs: float


class DismissalDetails(CCBaseModel):
    id: str
    text: str
    short_text: str
    innings: DismissalDetailsInnings
    over: DismissalDetailsOver


class Dismissal(CCBaseModel):
    bowler: Optional[AthleteWithFirstAndLastName] = None
    details: Optional[DismissalDetails] = None
    dismissal_card: str
    fielders: list[DismissalFielder]
    short_text: str
