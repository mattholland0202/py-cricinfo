from pycricinfo.models.source.api.common import CCBaseModel, Link, Position, RefMixin


class Flag(RefMixin):
    alt: str
    height: int
    rel: list[str]
    width: int


class Official(CCBaseModel):
    display_name: str
    flag: Flag
    links: Link
    order: int
    position: Position
