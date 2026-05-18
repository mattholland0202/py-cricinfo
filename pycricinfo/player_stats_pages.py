import asyncio
import re
from typing import Optional, Type

import aiohttp
from bs4 import BeautifulSoup, Tag

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


async def get_player_career(
    player_id: int,
    session: Optional[aiohttp.ClientSession] = None,
) -> Career:
    """
    Fetch and parse a player's international career stats from the Statsguru stats pages.

    Fetches batting, bowling, and fielding pages concurrently and merges them into a
    single Career object. Only Test, ODI, and T20I rows are extracted.

    Parameters
    ----------
    player_id : int
        Cricinfo player ID.
    session : aiohttp.ClientSession, optional
        An existing session to reuse. If None, one is created and closed after the request.

    Returns
    -------
    Career
        Structured career stats merged from all three stat types.
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
    return await get_request(
        route=get_settings().page_routes.player_stats,
        params={"player_id": str(player_id), "stat_type": stat_type},
        base_route=BaseRoute.stats,
        response_output_sub_folder="player_stats",
        session=session,
    )


# Generic parser for career summary rows
def _parse_career_summary_rows(html: str, row_model: Type[CareerStatsBaseModel]) -> list[CareerStatsBaseModel]:
    """
    Generic parser for Test/ODI/T20I career summary rows from a Statsguru stats page.
    row_model: The model class to instantiate for each row (e.g., CareerBattingRow, CareerBowlingRow)
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

    # Fallback for single-format pages where career summary rows are not grouped by format.
    if result:
        return result

    fallback_row = _extract_overall_career_averages_row(html)
    fallback_format = _extract_single_format_from_stats_tab(html)
    if not fallback_row or fallback_format is None:
        return result

    cells, headers = fallback_row
    if all((c.strip() == "-" or c.strip() == "") for c in cells):
        return result

    mapped = _map_cells(headers, cells)
    mapped["format"] = fallback_format
    result.append(row_model(**mapped))
    return result


def _extract_overall_career_averages_row(html: str) -> Optional[tuple[list[str], list[str]]]:
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
        return cell_texts, headers

    return None


def _extract_single_format_from_stats_tab(html: str) -> Optional[MatchTypeNames]:
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
    try:
        parsed = MatchTypeNames(format_name)
    except ValueError:
        return None

    if parsed not in _INTERNATIONAL_MATCH_TYPES:
        return None

    return parsed


def _extract_career_summary_rows(html: str) -> list[tuple[str, list[str], list[str]]]:
    """
    Find the Career summary table in an HTML stats page and return rows for the 3
    international formats only.

    Returns a list of (format_name, cell_texts, header_texts) tuples, one per
    matched format row. The header and cell lists are aligned by column index.
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

    # Only the first <tbody> holds the format-level grouping rows
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
    """
    a_tag = th.find("a")
    if a_tag:
        # Join only bare text nodes (NavigableString), which excludes <img> alt attributes
        return "".join(a_tag.strings).strip()
    return th.get_text(strip=True)


def _map_cells(headers: list[str], cells: list[str]) -> dict:
    """
    Zip headers with cell values and produce a dict whose keys match model
    validation aliases (which must match the table headers exactly).
    """
    return {header: value for header, value in zip(headers, cells) if value}
