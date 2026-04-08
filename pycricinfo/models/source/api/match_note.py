from typing import Optional

from pydantic import Field

from pycricinfo.models.source.api.common import CCBaseModel, DateMixin, RefMixin
from pycricinfo.types.match_types import MatchNoteType


class MatchNoteItem(CCBaseModel):
    """
    An item in a match note, which is used for player replacement notes. It contains the team name and the text
    describing the replacement.
    """

    team_name: str = Field(description="The name of the team that the note refers to")
    text: list[str] = Field(
        description="The text describing the player replacement. Seems to be of length 1.",
    )


class MatchNote(DateMixin, RefMixin):
    """
    A match note, which covers various types of event from the match, such as close of play scores, scoring milestones,
    and player replacements. The type of the note is determined by the 'type' field, and the content of the note is
    determined by the 'text' and 'items' fields.
    """

    id: Optional[str | int] = Field(default=None, description="Optional Cricinfo ID of the match note, if available")
    day_number: Optional[str | int] = Field(
        default=None,
        description="The day number of the match which the note refers to. Usually present for 'close of play' notes",
    )
    text: Optional[str] = Field(
        default=None, description="The text of the match note, for non-player replacement notes"
    )
    type: MatchNoteType = Field(description="The type of the match note")
    items: Optional[list[MatchNoteItem]] = Field(
        default=None,
        description=(
            "For player replacement notes, the format is a list of items with the team name and the text "
            "describing the replacement"
        ),
    )

    def __str__(self):
        if self.text:
            return self.text
        elif self.items:
            return self.items[0].text[0]  # This is the format for player replacement notes
        else:
            return f"MatchNote(id={self.id}, type={self.type})"
