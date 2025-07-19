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


class MatchResult(BaseModel):
    id: int
    description: str
    innings_1_info: Optional[str] = None
    innings_2_info: Optional[str] = None
    status: Optional[str] = None
