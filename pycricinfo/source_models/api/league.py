from pydantic import Field

from pycricinfo.source_models.api.common import CCBaseModel, Link


class League(CCBaseModel):
    id: int = Field(description="The Cricinfo ID for the league", examples=["123"])
    name: str = Field(description="The name of the league", examples=["Indian Premier League"])
    short_name: str = Field(description="A short name for the league", examples=["IPL"])
    abbreviation: str = Field(description="The abbreviation for the league", examples=["England tour of India 2020-21"])
    league_type: str = Field(description="The type of league", examples=["Primary"])
    is_tournament: bool = Field(description="Whether the league is a tournament")
    links: list[Link] = Field(description="Links related to the league")
