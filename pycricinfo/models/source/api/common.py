from abc import ABC
from typing import Optional

from pydantic import AliasChoices, AliasGenerator, BaseModel, ConfigDict, Field, HttpUrl, model_validator
from pydantic.alias_generators import to_camel


class CCBaseModel(ABC, BaseModel):
    """
    Abstract base class for Common Cricinfo (CC) models, which adds a validator so that the source data which
    contains camelCased fields can be deserialised into models with snake_case fields, and which sets any fields
    whose values are empty dictionaries to have a value of None
    """

    model_config = ConfigDict(
        alias_generator=AliasGenerator(validation_alias=to_camel), validate_by_name=True, validate_by_alias=True
    )

    @model_validator(mode="before")
    @classmethod
    def set_empty_dicts_to_none(self, data: dict):
        if not data:
            return data

        for k, v in data.items():
            if isinstance(v, dict) and len(v) == 0:
                data[k] = None
        return data


class PagingModel(CCBaseModel):
    """
    Details of paging information, included in any APIs which page their responses
    """

    count: int
    page_index: int
    page_size: int
    page_count: int


class RefMixin(CCBaseModel):
    """
    Mixin property of a URL included within models as a direct link to that entity
    """

    ref: Optional[HttpUrl] = Field(
        default=None,
        validation_alias=AliasChoices("ref", "$ref", "href"),
        description="The url to the entity, which is usually a link to ESPN's CDN",
    )


class DateMixin(CCBaseModel):
    """
    Mixin property for a date
    """

    date: Optional[str] = None


class DisplayNameMixin(BaseModel):
    """
    Mixin property for a display name
    """

    display_name: str


class Link(CCBaseModel):
    """
    All details of a link to an entity
    """

    language: Optional[str] = None
    rel: Optional[list[str] | str] = None
    href: HttpUrl
    text: str
    short_text: Optional[str] = None
    is_external: Optional[bool] = None
    is_premium: Optional[bool] = None


class Position(RefMixin):
    """
    A Player's position, which can represent both their overall role and their position within a match
    """

    displayName: Optional[str] = None
    id: Optional[str] = None
    name: Optional[str] = None
    abbreviation: Optional[str] = None


class Event(RefMixin, DateMixin):
    """
    An event, containing a link and a date
    """

    pass


class MatchClass(CCBaseModel):
    """
    The class (i.e. level and type) of a match
    """

    name: str
    event_type: str
    general_class_id: int
    general_class_card: Optional[str] = None
    international_class_id: Optional[int] = None
    international_class_card: Optional[str] = None


class FlagMixin(RefMixin):
    """
    Mixin property for a flag, for a person's nationality
    """

    alt: str
    rel: list[str]
    height: int
    width: int
