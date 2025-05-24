from typing import Optional

from pydantic import BaseModel, model_validator

from cricinfo.output_models.common import HeaderlessTableMixin
from cricinfo.source_models.commentary import APIResponseCommentary


class BallByBallPage(BaseModel, HeaderlessTableMixin):
    match_title: Optional[str]
    details: Optional[str]
    deliveries: list

    @model_validator(mode="before")
    @classmethod
    def create(cls, data: dict):
        page: APIResponseCommentary = data["page"]

        for item in page.commentary.items:
            pass
