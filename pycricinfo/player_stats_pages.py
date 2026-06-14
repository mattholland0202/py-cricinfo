import asyncio
import re
from typing import Optional, Type

import aiohttp
from bs4 import BeautifulSoup, Tag
from pydantic import BaseModel

from pycricinfo.api_helper import create_session, get_request
from pycricinfo.config import BaseRoute, get_settings
from pycricinfo.models.source.pages.player import (
    Career,
    CareerBattingRow,
    CareerBowlingRow,
    CareerFieldingRow,
    CareerStatsBaseModel,
)
from pycricinfo.types.match_types import MatchTypeNames

_INTERNATIONAL_MATCH_TYPES = frozenset({MatchTypeNames.TESTS, MatchTypeNames.ODIs, MatchTypeNames.T20Is})


class CareerAveragesRow(BaseModel):
    """Parsed overall row from the Career averages table."""

    headers: list[str]
    cells: list[str]


async def get_player_career(
    player_id: int,
    session: Optional[aiohttp.ClientSession] = None,
) -> Career:
    """
    Fetch and parse a player's international career stats from the Statsguru pages.

    Fetches batting, bowling, and fielding pages concurrently and returns a single Career object containing
    parsed batting, bowling, and fielding rows entries for Tests, ODIs, and T20Is.

    Parameters
    ----------
    player_id : int
        Cricinfo player ID.
    session : aiohttp.ClientSession, optional
        An existing session to reuse. If None, one is created and closed after the request.

    Returns
    -------
    Career
        Structured career stats from the three international match types.
    """
    owned_session = session is None
    if owned_session:
        session = create_session()

    try:
        # TODO: This only works for male players, there's no collective "all international formats" page for women
        batting_html, bowling_html, fielding_html = await asyncio.gather(
            _fetch_stats_page(player_id, "batting", session),
            _fetch_stats_page(player_id, "bowling", session),
            _fetch_stats_page(player_id, "fielding", session),
        )
    finally:
        if owned_session:
            await session.close()

    batting_rows = _parse_career_summary_rows(str(batting_html), CareerBattingRow)
    bowling_rows = _parse_career_summary_rows(str(bowling_html), CareerBowlingRow)
    fielding_rows = _parse_career_summary_rows(str(fielding_html), CareerFieldingRow)

    return Career(batting=batting_rows, bowling=bowling_rows, fielding=fielding_rows)


async def _fetch_stats_page(player_id: int, stat_type: str, session: aiohttp.ClientSession) -> str:
    """
    Fetch a single Statsguru player page.

    Parameters
    ----------
    player_id : int
        Cricinfo player ID.
    stat_type : str
        One of the supported player stat page types: batting, bowling, or fielding.
    session : aiohttp.ClientSession
        Open HTTP session used for the request.

    Returns
    -------
    str
        HTML response body for the requested stats page.
    """
    return await get_request(
        route=get_settings().page_routes.player_stats,
        params={"player_id": str(player_id), "stat_type": stat_type},
        base_route=BaseRoute.stats,
        response_output_sub_folder="player_stats",
        session=session,
    )


def _parse_career_summary_rows(html: str, row_model: Type[CareerStatsBaseModel]) -> list[CareerStatsBaseModel]:
    """
    Parse career rows from a Statsguru page into a typed list of models.

    The parser first tries the grouped Career summary table. If the page only exposes
    a single international format, it falls back to the overall row in Career averages
    and uses the single statsTab entry to determine the format.

    Parameters
    ----------
    html : str
        HTML content for the relevant Statsguru player stats page.
    row_model : Type[CareerStatsBaseModel]
        Model class to instantiate for each row.

    Returns
    -------
    list[CareerStatsBaseModel]
        Parsed career rows for one or more international formats.
    """
    try:
        rows = _extract_career_summary_rows(html)
    except Exception:
        rows = []
    result: list[CareerStatsBaseModel] = []

    for format_name, cells, headers in rows:
        if all((c.strip() == "-" or c.strip() == "") for c in cells):
            continue
        format_value = _to_international_match_type(format_name)
        if format_value is None:
            continue
        mapped = _map_cells(headers, cells)
        mapped["format"] = format_value
        result.append(row_model(**mapped))

    # Fallback for single-format pages where career summary rows are not grouped by format,
    # which will be the case if the player has only played one format of international cricket.
    if result:
        return result

    fallback_row = _extract_overall_career_averages_row(html)
    fallback_format = _extract_single_format_from_stats_tab(html)
    if not fallback_row or fallback_format is None:
        return result

    if all((c.strip() == "-" or c.strip() == "") for c in fallback_row.cells):
        return result

    mapped = _map_cells(fallback_row.headers, fallback_row.cells)
    mapped["format"] = fallback_format
    result.append(row_model(**mapped))
    return result


def _extract_overall_career_averages_row(html: str) -> Optional[CareerAveragesRow]:
    """
    Extract the overall row from the Career averages table.

    Parameters
    ----------
    html : str
        HTML content for the player stats page.

    Returns
    -------
    Optional[CareerAveragesRow]
        The overall row cells and table headers, or None if not present.
    """
    soup = BeautifulSoup(html, "html.parser")

    caption = soup.find("caption", string=re.compile(r"^Career averages$", re.IGNORECASE))
    if not caption:
        return None

    table = caption.find_parent("table")
    if table is None:
        return None

    thead = table.find("thead")
    if thead is None:
        return None

    thead_row = thead.find("tr")
    if thead_row is None:
        return None

    headers = [_extract_th_text(th) for th in thead_row.find_all("th")]

    tbody = table.find("tbody")
    if tbody is None:
        return None

    for tr in tbody.find_all("tr"):
        cells = tr.find_all("td")
        if not cells:
            continue
        label = cells[0].get_text(strip=True).lower()
        if label != "overall":
            continue

        cell_texts = [td.get_text(strip=True) for td in cells]
        return CareerAveragesRow(headers=headers, cells=cell_texts)

    return None


def _extract_single_format_from_stats_tab(html: str) -> Optional[MatchTypeNames]:
    """
    Extract the single international format label from the statsTab navigation.

    Parameters
    ----------
    html : str
        HTML content for the player stats page.

    Returns
    -------
    Optional[MatchTypeNames]
        The mapped international match type if exactly one valid format is present,
        otherwise None.
    """
    soup = BeautifulSoup(html, "html.parser")

    stats_tab = soup.find("ul", id="statsTab")
    if stats_tab is None:
        return None

    labels = []
    for anchor in stats_tab.find_all("a"):
        text = anchor.get_text(" ", strip=True)
        if not text:
            continue
        label = re.sub(r"\s*\([^)]*\)\s*$", "", text).strip()
        format_value = _to_international_match_type(label)
        if format_value is not None:
            labels.append(format_value)

    if len(labels) != 1:
        return None

    return labels[0]


def _to_international_match_type(format_name: str) -> Optional[MatchTypeNames]:
    """
    Normalize a stats-page label to an international match type.

    Parameters
    ----------
    format_name : str
        Raw format label from the page, such as "Test matches", "Tests", or "ODIs".

    Returns
    -------
    Optional[MatchTypeNames]
        The corresponding international match type, or None when the label is not
        one of the supported international formats.
    """
    try:
        parsed = MatchTypeNames(format_name)
    except ValueError:
        return None

    if parsed not in _INTERNATIONAL_MATCH_TYPES:
        return None

    return parsed


def _extract_career_summary_rows(html: str) -> list[tuple[str, list[str], list[str]]]:
    """
    Find the Career summary table in an HTML stats page and return rows for the
    supported international formats.

    Returns a list of (format_name, cell_texts, header_texts) tuples, one per
    matched format row. The header and cell lists are aligned by column index.

    Parameters
    ----------
    html : str
        HTML content for the player stats page.

    Returns
    -------
    list[tuple[str, list[str], list[str]]]
        Grouped career summary rows, filtered to the supported international formats.
    """
    soup = BeautifulSoup(html, "html.parser")

    caption = soup.find("caption", string=re.compile(r"^Career summary$", re.IGNORECASE))
    if not caption:
        return []

    table = caption.find_parent("table")
    if table is None:
        return []

    thead = table.find("thead")
    if thead is None:
        return []
    thead_row = thead.find("tr")
    if thead_row is None:
        return []
    headers = [_extract_th_text(th) for th in thead_row.find_all("th")]

    first_tbody = table.find("tbody")
    if first_tbody is None:
        return []
    result = []
    for tr in first_tbody.find_all("tr"):
        cells = tr.find_all("td")
        if not cells:
            continue

        b_tag = cells[0].find("b")
        if not b_tag:
            continue

        format_name = b_tag.get_text(strip=True)
        if _to_international_match_type(format_name) is None:
            continue

        cell_texts = [td.get_text(strip=True) for td in cells]
        result.append((format_name, cell_texts, headers))

    return result


def _extract_th_text(th: Tag) -> str:
    """
    Extract a column header's display text, ignoring any <img> alt text.
    Header cells contain anchor links whose text may be followed by a sort-indicator image.

    Parameters
    ----------
    th : Tag
        Header cell element.

    Returns
    -------
    str
        Visible header text.
    """
    a_tag = th.find("a")
    if a_tag:
        return "".join(a_tag.strings).strip()
    return th.get_text(strip=True)


def _map_cells(headers: list[str], cells: list[str]) -> dict:
    """
    Zip headers with cell values and produce a dict whose keys match model
    validation aliases (which must match the table headers exactly).

    Parameters
    ----------
    headers : list[str]
        Column header names.
    cells : list[str]
        Cell values for a single row.

    Returns
    -------
    dict
        Mapping of non-empty header/value pairs.
    """
    return {header: value for header, value in zip(headers, cells) if value}
