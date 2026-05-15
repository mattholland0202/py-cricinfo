import re
from typing import Optional, TypeVar
from urllib.parse import quote

import aiohttp
from bs4 import BeautifulSoup, Tag

from pycricinfo.api_helper import get_request
from pycricinfo.config import BaseRoute, get_settings
from pycricinfo.models.source.pages.player import (
    Career,
    CareerBattingFieldingRow,
    CareerBowlingRow,
    CareerStatsBaseModel,
)

CareerRowT = TypeVar("CareerRowT", bound=CareerStatsBaseModel)


async def get_player_career_stats(
    player_name: str,
    player_id: int,
    session: Optional[aiohttp.ClientSession] = None,
) -> Career:
    """
    Fetch and parse a player's career stats tables.

    Parameters
    ----------
    player_name : str
        Player name for the URL, for example "Ben Stokes".
    player_id : int
        Cricinfo player ID in the URL.
    session : aiohttp.ClientSession, optional
        An existing session to use for the request, by default None.

    Returns
    -------
    Career
        Structured career batting/fielding and bowling rows.
    """
    player_slug = _slugify_player_name(player_name)
    content = await get_request(
        route=get_settings().page_routes.player_profile,
        params={"player_slug": player_slug, "player_id": str(player_id)},
        base_route=BaseRoute.page,
        warm_session=False,
        session=session,
    )
    return _parse_player_career_stats_page(str(content))


def _slugify_player_name(player_name: str) -> str:
    """
    Convert a player name into the Cricinfo URL slug format.

    Parameters
    ----------
    player_name : str
        Raw player name, for example "Ben Stokes".

    Returns
    -------
    str
        URL-safe slug, for example "ben-stokes".
    """
    name = re.sub(r"\s+", "-", player_name.strip().lower())
    return quote(name, safe="-")


def _parse_player_career_stats_page(content: str) -> Career:
    """
    Parse the "Career Stats" section from a player profile page.

    Parameters
    ----------
    content : str
        Raw HTML of a player's profile page.

    Returns
    -------
    Career
        Structured career batting/fielding and bowling rows.
    """
    soup = BeautifulSoup(content, "html.parser")
    career_section = _find_career_stats_section(soup)

    batting_table = _find_table_in_section(career_section, "Batting & Fielding")
    bowling_table = _find_table_in_section(career_section, "Bowling")

    batting_rows = _parse_table_rows(batting_table, CareerBattingFieldingRow)
    bowling_rows = _parse_table_rows(bowling_table, CareerBowlingRow)

    return Career(batting_and_fielding=batting_rows, bowling=bowling_rows)


def _find_career_stats_section(soup: BeautifulSoup) -> Tag:
    """
    Find the container element that wraps the "Career Stats" section.

    Parameters
    ----------
    soup : BeautifulSoup
        Parsed player page HTML.

    Returns
    -------
    bs4.Tag
        Section tag containing both batting and bowling career tables.

    Raises
    ------
    ValueError
        If the heading or section container cannot be found.
    """
    heading = soup.find("h2", string=re.compile(r"career\s+stats", re.IGNORECASE))
    if not heading:
        raise ValueError("Unable to find 'Career Stats' heading in player page")

    section = heading.find_parent("div", class_=lambda c: c and "ds-bg-fill-content-prime" in c)
    if not section:
        raise ValueError("Unable to find container for 'Career Stats' section")

    return section


def _find_table_in_section(section: Tag, title: str) -> Tag:
    """
    Find a specific table in the career stats section by table heading text.

    Parameters
    ----------
    section : bs4.Tag
        Career stats section returned by _find_career_stats_section.
    title : str
        Exact visible heading text for the desired table.

    Returns
    -------
    bs4.Tag
        The matching table element.

    Raises
    ------
    ValueError
        If the heading or table cannot be found.
    """
    title_node = section.find("p", string=re.compile(rf"^{re.escape(title)}$", re.IGNORECASE))
    if not title_node:
        raise ValueError(f"Unable to find '{title}' table heading in 'Career Stats' section")

    table = title_node.find_next("table")
    if not table:
        raise ValueError(f"Unable to find table for '{title}' in 'Career Stats' section")

    return table


def _parse_table_rows(table: Tag, model_cls: type[CareerRowT]) -> list[CareerRowT]:
    """
    Parse all rows from a career stats table into strongly typed model instances.

    Parameters
    ----------
    table : bs4.Tag
        Source table element.
    model_cls : type[CareerRowT]
        Row model class used to validate and store each parsed row.

    Returns
    -------
    list[CareerRowT]
        Parsed and validated row models.
    """
    headers = [h.get_text(strip=True) for h in table.select("thead th")]
    normalized_headers = [_normalize_header_text(h) for h in headers]

    rows = []
    for row in table.select("tbody tr"):
        cells = [c.get_text(strip=True) for c in row.find_all("td")]
        if not cells:
            continue

        mapped_data = {}
        for header, value in zip(normalized_headers, cells):
            if header:
                mapped_data[header] = value

        if "format" in mapped_data:
            rows.append(model_cls(**mapped_data))

    return rows


def _normalize_header_text(header_text: str) -> str:
    """
    Normalize table header text to a stable key for model population.

    Parameters
    ----------
    header_text : str
        Raw header cell text from the HTML table.

    Returns
    -------
    str
        Lower-cased, whitespace-free key with '&' normalized to 'and'.
    """
    text = header_text.strip().lower()
    text = text.replace("&", "and")
    return re.sub(r"\s+", "", text)
