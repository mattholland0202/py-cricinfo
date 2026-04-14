from typing import Optional

from pydantic import AliasChoices, BaseModel, Field, computed_field

from pycricinfo.models.source.api.athelete import AthleteWithNameAndShortName as Athlete
from pycricinfo.models.source.api.common import CCBaseModel, PagingModel
from pycricinfo.models.source.api.team import TeamWithName as Team


class CommentaryPlayType(BaseModel):
    id: str
    description: str


class CommentaryBowler(BaseModel):
    athlete: Optional[Athlete] = Field(default=None)
    team: Team
    maidens: int
    balls: int
    wickets: int
    overs: float
    conceded: int


class CommentaryBatter(CCBaseModel):
    athlete: Athlete
    team: Team
    total_runs: int
    faced: int
    fours: int
    runs: int
    sixes: int


class CommentaryInnings(CCBaseModel):
    id: str
    run_rate: float
    remaining_balls: int
    byes: int
    number: int
    balls: int
    no_balls: int
    wickets: int
    leg_byes: int
    ball_limit: int
    target: int
    session: int
    day: int
    fall_of_wickets: int
    trail_by: int
    lead_by: int
    remaining_overs: float
    total_runs: int
    wides: int
    runs: int

    @computed_field
    @property
    def current_score(self) -> str:
        return f"{self.runs}/{self.wickets}"


class CommentaryOver(CCBaseModel):
    ball: int
    balls: int
    complete: bool
    limit: float
    maiden: int
    no_ball: int
    wide: int
    leg_byes: int
    byes: int
    number: int
    runs: int
    wickets: int
    overs: float
    actual: float
    unique: float


class CommentaryDismissalAthlete(CCBaseModel):
    athlete: Athlete


class CommentaryFielderAthlete(CommentaryDismissalAthlete):
    is_keeper: bool


class CommentaryDismissal(CCBaseModel):
    dismissal: bool
    bowled: bool
    type: str
    bowler: CommentaryDismissalAthlete
    batter: CommentaryDismissalAthlete = Field(validation_alias=AliasChoices("batter", "batsman"))
    fielder: Optional[CommentaryFielderAthlete] = None
    text: str
    minutes: Optional[int | str] = None
    retired_text: str


class CommentaryDelivery(CCBaseModel):
    id: str
    clock: str
    date: str
    play_type: CommentaryPlayType
    team: Team
    media_id: int
    period: int
    period_text: str
    pre_text: str
    text: str
    post_text: str
    short_text: str
    home_score: str
    away_score: str
    score_value: int
    sequence: int
    athletes_involved: list[Athlete]
    speed_kph: Optional[float] = None
    speed_mph: Optional[float] = None
    bowler: CommentaryBowler
    other_bowler: Optional[CommentaryBowler] = None
    batter: CommentaryBatter = Field(validation_alias=AliasChoices("batter", "batsman"))
    other_batter: CommentaryBatter = Field(
        validation_alias=AliasChoices("other_batter", "other_batsman", "otherBatsman")
    )
    current_innings_score: CommentaryInnings = Field(validation_alias=AliasChoices("current_innings_score", "innings"))
    over: CommentaryOver
    dismissal: CommentaryDismissal
    bbb_timestamp: int

    @computed_field
    @property
    def short_summary(self) -> str:
        return f"{self.over.overs}: {self.short_text} - {self.current_innings_score.current_score}"


class Commentary(PagingModel):
    """The data about the current page, and the list of deliveries"""

    deliveries: list[CommentaryDelivery] = Field(validation_alias=AliasChoices("items", "deliveries"))


class APIResponseCommentary(BaseModel):
    """The API response contains a root field called 'commentary' which contains the actual commentary data."""

    commentary: Commentary
