"""Models for series and match listings, scraped from season and series pages."""

from pydantic import BaseModel, Field


class MatchSeries(BaseModel):
    """A series listed on a season page."""

    series_id: int
    data_series_id: int
    title: str
    link: str
    summary_url: str


class MatchTypeWithSeries(BaseModel):
    """A type of match, such as Tests or ODIs, with the series of that type in a season."""

    name: str
    series: list[MatchSeries] | None = Field(default_factory=list)


class MatchResult(BaseModel):
    """A match listed on a series page, with its scores and result."""

    id: int
    description: str
    innings_1_info: str | None = None
    innings_2_info: str | None = None
    status: str | None = None
