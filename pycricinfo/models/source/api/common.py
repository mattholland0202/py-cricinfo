"""Base model and common fields shared by the API source models."""

from abc import ABC
from typing import Annotated, TypeVar

from pydantic import (
    AliasChoices,
    AliasGenerator,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    HttpUrl,
    model_validator,
)
from pydantic.alias_generators import to_camel


class CCBaseModel(ABC, BaseModel):
    """
    Abstract base class for Common Cricinfo (CC) models.

    It generates aliases so that the source data, which contains camelCased fields, can be deserialised into models
    with snake_case fields, and adds a validator which sets any fields whose values are empty dictionaries to None.
    """

    model_config = ConfigDict(
        alias_generator=AliasGenerator(validation_alias=to_camel), validate_by_name=True, validate_by_alias=True
    )

    @model_validator(mode="before")
    @classmethod
    def set_empty_dicts_to_none(cls, data: dict) -> dict:
        """
        Replace any empty dictionaries in the source data with None.

        Parameters
        ----------
        data : dict
            The source data being validated

        Returns
        -------
        dict
            The data, with empty dictionaries replaced
        """
        if not data:
            return data

        for k, v in data.items():
            if isinstance(v, dict) and len(v) == 0:
                data[k] = None
        return data


T = TypeVar("T")


def falsy_to_none(x: object) -> object:
    """
    Replace a falsy value, such as an empty dictionary or string, with None.

    Parameters
    ----------
    x : object
        The value to check

    Returns
    -------
    object
        The value, or None if it was falsy
    """
    return x or None


LeniantOptional = Annotated[T | None, BeforeValidator(falsy_to_none)]


class PagingModel(CCBaseModel):
    """Details of paging information, included in any APIs which page their responses."""

    count: int
    page_index: int
    page_size: int
    page_count: int


class RefMixin(CCBaseModel):
    """Mixin property of a URL included within models as a direct link to that entity."""

    ref: HttpUrl | None = Field(
        default=None,
        validation_alias=AliasChoices("ref", "$ref", "href"),
        description="The url to the entity, which is usually a link to ESPN's CDN",
    )


class DateMixin(CCBaseModel):
    """Mixin property for a date."""

    date: str | None = None


class DisplayNameMixin(BaseModel):
    """Mixin property for a display name."""

    display_name: str


class Link(CCBaseModel):
    """All details of a link to an entity."""

    language: str | None = None
    rel: list[str] | str | None = None
    href: HttpUrl
    text: str
    short_text: str | None = None
    is_external: bool | None = None
    is_premium: bool | None = None


class Position(RefMixin):
    """A Player's position, which can represent both their overall role and their position within a match."""

    display_name: str | None = None
    id: str | None = None
    name: str | None = None
    abbreviation: str | None = None


class Event(RefMixin, DateMixin):
    """An event, containing a link and a date."""


class MatchClass(CCBaseModel):
    """The class (i.e. level and type) of a match."""

    name: str
    event_type: str
    general_class_id: int
    general_class_card: str | None = None
    international_class_id: int | None = None
    international_class_card: str | None = None


class FlagMixin(RefMixin):
    """Mixin property for a flag, for a person's nationality."""

    alt: str
    rel: list[str]
    height: int
    width: int
