from pydantic import AliasChoices, BaseModel, Field, computed_field

from pycricinfo.source_models.api.statistics import PlayerStatisticsCategory


class PlayerMatchInningsDetails(BaseModel):
    period: int
    media_id: int = Field(validation_alias=AliasChoices("media_id", "mediaId"))
    statistics: PlayerStatisticsCategory

    def find(self, name: str) -> int | str | float:
        return self.statistics.find(name)

    @computed_field
    @property
    def batted(self) -> bool:
        return self.find("batted")

    @computed_field
    @property
    def bowled(self) -> bool:
        return self.find("bowled")
