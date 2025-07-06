from typing import Optional

from pydantic import BaseModel, Field


class MatchSeries(BaseModel):
    title: str
    id: str
    link: str
    summary_url: str


class MatchType(BaseModel):
    name: str
    series: Optional[list[MatchSeries]] = Field(default_factory=list)
