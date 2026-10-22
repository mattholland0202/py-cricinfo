"""Models for match officials."""

from pycricinfo.models.source.api.common import CCBaseModel, FlagMixin, Link, Position


class Official(CCBaseModel):
    """A match official, such as an umpire or match referee."""

    display_name: str
    flag: FlagMixin
    links: Link
    order: int
    position: Position
