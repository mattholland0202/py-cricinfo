from pydantic import BaseModel


class Series(BaseModel):
    title: str
    id: str
    link: str
    summary_url: str
