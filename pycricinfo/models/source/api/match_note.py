from typing import Optional

from pydantic import Field, HttpUrl

from pycricinfo.models.source.api.common import CCBaseModel
from pycricinfo.types.match_types import MatchNoteType


class MatchNote(CCBaseModel):
    id: Optional[str | int] = Field(default=None)
    day_number: Optional[str | int] = Field(default=None)
    date: Optional[str] = Field(default=None)
    text: Optional[str] = Field(default=None)
    type: MatchNoteType
    href: Optional[HttpUrl] = Field(default=None)
