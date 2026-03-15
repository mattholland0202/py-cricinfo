from typing import Optional

from pydantic import Field, HttpUrl

from pycricinfo.models.source.api.common import DateMixin
from pycricinfo.types.match_types import MatchNoteType


class MatchNote(DateMixin):
    id: Optional[str | int] = Field(default=None)
    day_number: Optional[str | int] = Field(default=None)
    text: Optional[str] = Field(default=None)
    type: MatchNoteType
    href: Optional[HttpUrl] = Field(default=None)
