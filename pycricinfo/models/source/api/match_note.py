from typing import Optional

from pydantic import Field

from pycricinfo.models.source.api.common import DateMixin, RefMixin
from pycricinfo.types.match_types import MatchNoteType


class MatchNote(DateMixin, RefMixin):
    id: Optional[str | int] = Field(default=None)
    day_number: Optional[str | int] = Field(default=None)
    text: Optional[str] = Field(default=None)
    type: MatchNoteType
