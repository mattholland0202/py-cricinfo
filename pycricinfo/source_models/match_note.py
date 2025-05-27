from typing import Optional

from pydantic import Field, HttpUrl

from pycricinfo.source_models.common import CCBaseModel


class MatchNote(CCBaseModel):
    id: Optional[str | int] = Field(default=None)
    day_number: Optional[str] = Field(default=None)
    date: Optional[str] = Field(default=None)
    text: str
    type: str
    href: Optional[HttpUrl] = Field(default=None)
