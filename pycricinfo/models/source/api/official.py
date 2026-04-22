from pycricinfo.models.source.api.common import CCBaseModel, FlagMixin, Link, Position


class Official(CCBaseModel):
    display_name: str
    flag: FlagMixin
    links: Link
    order: int
    position: Position
