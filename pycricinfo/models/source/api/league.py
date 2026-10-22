"""Models for leagues."""

from pydantic import Field

from pycricinfo.models.source.api.common import CCBaseModel, Link


class League(CCBaseModel):
    """A league, which in Cricinfo's API represents a series or tournament."""

    id: int = Field(description="The Cricinfo ID for the league", examples=["123"])
    name: str = Field(description="The name of the league", examples=["Indian Premier League"])
    short_name: str = Field(description="A short name for the league", examples=["IPL"])
    abbreviation: str = Field(description="The abbreviation for the league", examples=["England tour of India 2020-21"])
    league_type: str = Field(description="The type of league", examples=["Primary"])
    is_tournament: bool = Field(description="Whether the league is a tournament")
    links: list[Link] = Field(description="Links related to the league")
