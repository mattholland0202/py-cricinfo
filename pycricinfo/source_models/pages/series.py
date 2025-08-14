from typing import Optional

from pydantic import BaseModel, Field


class MatchSeries(BaseModel):
    series_id: int
    data_series_id: int
    title: str
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
