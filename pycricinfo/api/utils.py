"""Shared dependencies for the FastAPI endpoints."""

from typing import Annotated

from fastapi import Query


class PageAndInningsQueryParameters:
    """Query parameters for which innings, and which page within it, to get ball-by-ball data for."""

    def __init__(
        self,
        innings: Annotated[int, Query(description="Which innings of the game to get data from")] = 1,
        page: Annotated[int, Query(description="Which page of data to return")] = 1,
    ) -> None:
        self.page = page
        self.innings = innings
