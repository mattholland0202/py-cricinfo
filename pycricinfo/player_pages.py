import re
from typing import Optional
from urllib.parse import quote

import aiohttp
from bs4 import BeautifulSoup, Tag

from pycricinfo.api_helper import create_session, fetch_page_content, warm_page_session
from pycricinfo.exceptions import CricinfoAPIException
from pycricinfo.models.source.pages.player import Career, CareerBattingFieldingRow, CareerBowlingRow

BATTING_FIELD_MAPPING = {
    "format": "format",
    "mat": "matches",
    "inns": "innings",
    "no": "not_outs",
    "runs": "runs",
    "hs": "highest_score",
    "ave": "average",
    "bf": "balls_faced",
    "sr": "strike_rate",
    "100s": "centuries",
    "50s": "half_centuries",
    "4s": "fours",
    "6s": "sixes",
    "ct": "catches",
    "st": "stumpings",
}

BOWLING_FIELD_MAPPING = {
    "format": "format",
    "mat": "matches",
    "inns": "innings",
    "balls": "balls_bowled",
    "runs": "runs_conceded",
    "wkts": "wickets",
    "bbi": "best_bowling_innings",
    "bbm": "best_bowling_match",
    "ave": "average",
    "econ": "economy_rate",
    "sr": "strike_rate",
    "4w": "four_wicket_hauls",
    "5w": "five_wicket_hauls",
    "10w": "ten_wicket_hauls",
}


async def get_player_page_content(
    player_name: str,
    player_id: int,
    session: Optional[aiohttp.ClientSession] = None,
) -> str:
    """
    Fetch the HTML for an ESPN Cricinfo player profile page.

    Parameters
    ----------
    player_name : str
        Player name from the URL, for example "Ben Stokes".
    player_id : int
        Cricinfo player ID in the URL.
    session : aiohttp.ClientSession, optional
        An existing session to use for the request, by default None.

    Returns
    -------
    str
        HTML content of the player profile page.
    """
    player_slug = _slugify_player_name(player_name)
    profile_url = f"https://www.espncricinfo.com/cricketers/{player_slug}-{player_id}"

    owned_session = session is None
    if owned_session:
        session = create_session()

    try:
        # Warm cookies/session first; this can reduce bot/WAF challenges on direct profile-page hits.
        await warm_page_session(session)

        content, status = await fetch_page_content(session, profile_url)

        if status == 200:
            return content

        raise CricinfoAPIException(status_code=status, route=profile_url, content=content)
    finally:
        if owned_session:
            await session.close()


def parse_player_career_stats_page(content: str) -> Career:
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

    batting_rows = _parse_table_rows(batting_table, BATTING_FIELD_MAPPING, CareerBattingFieldingRow)
    bowling_rows = _parse_table_rows(bowling_table, BOWLING_FIELD_MAPPING, CareerBowlingRow)

    return Career(batting_and_fielding=batting_rows, bowling=bowling_rows)


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
        Player name from the URL, for example "Ben Stokes".
    player_id : int
        Cricinfo player ID in the URL.
    session : aiohttp.ClientSession, optional
        An existing session to use for the request, by default None.

    Returns
    -------
    Career
        Structured career batting/fielding and bowling rows.
    """
    content = await get_player_page_content(player_name=player_name, player_id=player_id, session=session)
    return parse_player_career_stats_page(content)


def _slugify_player_name(player_name: str) -> str:
    name = re.sub(r"\s+", "-", player_name.strip().lower())
    return quote(name, safe="-")


def _find_career_stats_section(soup: BeautifulSoup) -> Tag:
    heading = soup.find("h2", string=re.compile(r"career\s+stats", re.IGNORECASE))
    if not heading:
        raise ValueError("Unable to find 'Career Stats' heading in player page")

    section = heading.find_parent("div", class_=lambda c: c and "ds-bg-fill-content-prime" in c)
    if not section:
        raise ValueError("Unable to find container for 'Career Stats' section")

    return section


def _find_table_in_section(section: Tag, title: str) -> Tag:
    title_node = section.find("p", string=re.compile(rf"^{re.escape(title)}$", re.IGNORECASE))
    if not title_node:
        raise ValueError(f"Unable to find '{title}' table heading in 'Career Stats' section")

    table = title_node.find_next("table")
    if not table:
        raise ValueError(f"Unable to find table for '{title}' in 'Career Stats' section")

    return table


def _parse_table_rows(table: Tag, field_mapping: dict[str, str], model_cls):
    headers = [h.get_text(strip=True) for h in table.select("thead th")]
    normalized_headers = [_normalize_header_text(h) for h in headers]

    rows = []
    for row in table.select("tbody tr"):
        cells = [c.get_text(strip=True) for c in row.find_all("td")]
        if not cells:
            continue

        mapped_data = {}
        for header, value in zip(normalized_headers, cells):
            field_name = field_mapping.get(header)
            if field_name:
                mapped_data[field_name] = value

        if "format" in mapped_data:
            rows.append(model_cls(**mapped_data))

    return rows


def _normalize_header_text(header_text: str) -> str:
    text = header_text.strip().lower()
    text = text.replace("&", "and")
    return re.sub(r"\s+", "", text)
