from typing import Annotated

from fastapi import Query


class PageAndInningsQueryParameters:
    def __init__(
        self,
        page: Annotated[int, Query(description="Which page of data to return")] = 1,
        innings: Annotated[int, Query(description="Which innings of the game to get data from")] = 1,
    ):
        self.page = page
        self.innings = innings
