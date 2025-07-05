from enum import Enum
from typing import Optional

from pydantic import Field, HttpUrl

from pycricinfo.source_models.api.common import CCBaseModel


class MatchNoteType(Enum):
    SERIES_NOTE = "seriesnote"
    POINTS = "points"
    MATCH_NUMBER = "matchnumber"
    SEASON = "season"
    MATCH_DAYS = "matchdays"
    TOSS = "toss"
    LIVE_COMMENTATOR = "livecommentator"
    LIVE_SCORER = "livescorer"
    MATCH_NOTE = "matchnote"
    CLOSE_OF_PLAY = "closeofplay"
    HOURS_OF_PLAY = "hoursofplay"


class MatchNote(CCBaseModel):
    id: Optional[str | int] = Field(default=None)
    day_number: Optional[str] = Field(default=None)
    date: Optional[str] = Field(default=None)
    text: str
    type: MatchNoteType
    href: Optional[HttpUrl] = Field(default=None)
