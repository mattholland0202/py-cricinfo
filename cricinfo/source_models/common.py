from abc import ABC
from typing import Optional

from pydantic import AliasChoices, AliasGenerator, BaseModel, ConfigDict, Field, HttpUrl, model_validator
from pydantic.alias_generators import to_camel


class CCBaseModel(ABC, BaseModel):
    model_config = ConfigDict(alias_generator=AliasGenerator(validation_alias=to_camel))

    @model_validator(mode="before")
    @classmethod
    def set_empty_dicts_to_none(self, data: dict):
        for k, v in data.items():
            if isinstance(v, dict) and len(v) == 0:
                data[k] = None
        return data


class PagingModel(CCBaseModel):
    count: int
    pageIndex: int
    pageSize: int
    pageCount: int


class RefMixin(CCBaseModel):
    ref: Optional[HttpUrl] = Field(default=None, validation_alias=AliasChoices("ref", "$ref", "href"))


class DateMixin(CCBaseModel):
    date: Optional[str] = None


class IDMixin(BaseModel):
    id: str


class NameMixin(BaseModel):
    name: str


class DisplayNameMixin(BaseModel):
    display_name: str


class Link(CCBaseModel):
    language: Optional[str] = None
    rel: Optional[list[str] | str] = None
    href: HttpUrl
    text: str
    short_text: Optional[str] = None
    is_external: Optional[bool] = None
    is_premium: Optional[bool] = None


class Position(RefMixin):
    displayName: Optional[str] = None
    id: Optional[str] = None
    name: str
    abbreviation: Optional[str] = None


class Event(RefMixin, DateMixin): ...
