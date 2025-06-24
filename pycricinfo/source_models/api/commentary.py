from typing import Optional

from pydantic import AliasChoices, BaseModel, Field, computed_field

from pycricinfo.source_models.api.athelete import AthleteWithNameAndShortName as Athlete
from pycricinfo.source_models.api.common import CCBaseModel, PagingModel
from pycricinfo.source_models.api.team import TeamWithName as Team


class PlayType(BaseModel):
    id: str
    description: str


class Bowler(BaseModel):
    athlete: Optional[Athlete] = Field(default=None)
    team: Team
    maidens: int
    balls: int
    wickets: int
    overs: float
    conceded: int


class Batsman(CCBaseModel):
    athlete: Athlete
    team: Team
    total_runs: int
    faced: int
    fours: int
    runs: int
    sixes: int


class Innings(CCBaseModel):
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
    trailBy: int
    leadBy: int
    remaining_overs: float
    total_runs: int
    wides: int
    runs: int

    @computed_field
    @property
    def score(self) -> str:
        return f"{self.runs}/{self.wickets}"


class Over(CCBaseModel):
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


class BowlerAthlete(BaseModel):
    athlete: Athlete


class BatsmanAthlete(BaseModel):
    athlete: Athlete


class Dismissal(CCBaseModel):
    dismissal: bool
    bowled: bool
    type: str
    bowler: BowlerAthlete
    batsman: BatsmanAthlete
    text: str
    minutes: Optional[int | str] = None  # TODO: Can be empty string - parse to null in that case
    retired_text: str


class CommentaryItem(CCBaseModel):
    id: str
    clock: str
    date: str
    play_type: PlayType
    team: Team
    media_id: int
    period: int
    periodText: str
    preText: str
    text: str
    post_text: str
    short_text: str
    home_score: str
    away_score: str
    score_value: int
    sequence: int
    athletes_involved: list[Athlete]
    bowler: Bowler
    other_bowler: Optional[Bowler] = None
    batsman: Batsman
    other_batsman: Batsman
    current_innings_score: Innings = Field(validation_alias=AliasChoices("current_innings_score", "innings"))
    over: Over
    dismissal: Dismissal
    bbb_timestamp: int

    @computed_field
    @property
    def summary(self) -> str:
        return f"{self.over.overs}: {self.short_text} - {self.current_innings_score.score}"


class Commentary(PagingModel):
    items: list[CommentaryItem]


class APIResponseCommentary(BaseModel):
    commentary: Commentary
