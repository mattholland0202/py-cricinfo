"""Models for how a batter was dismissed."""

from pydantic import BaseModel

from pycricinfo.models.source.api.athelete import AthleteWithFirstAndLastName
from pycricinfo.models.source.api.common import CCBaseModel


class DismissalFielder(CCBaseModel):
    """A fielder involved in a dismissal."""

    athlete: AthleteWithFirstAndLastName
    display_order: int
    is_keeper: int
    is_substitute: int


class DismissalDetailsInnings(BaseModel):
    """The innings score at the point of a dismissal."""

    wickets: int
    runs: int


class DismissalDetailsOver(BaseModel):
    """The over in which a dismissal happened."""

    overs: float


class DismissalDetails(CCBaseModel):
    """Details of a dismissal, including when in the innings it happened."""

    id: str
    text: str
    short_text: str
    innings: DismissalDetailsInnings
    over: DismissalDetailsOver


class Dismissal(CCBaseModel):
    """How a batter was dismissed, including the bowler and any fielders involved."""

    bowler: AthleteWithFirstAndLastName | None = None
    details: DismissalDetails | None = None
    dismissal_card: str
    fielders: list[DismissalFielder]
    short_text: str
