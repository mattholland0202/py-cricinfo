import asyncio
import re
from typing import Optional

import aiohttp
from bs4 import BeautifulSoup, Tag

from pycricinfo.api_helper import create_session, get_request
from pycricinfo.config import BaseRoute, get_settings
from pycricinfo.models.source.pages.player import (
    Career,
    CareerBattingFieldingRow,
    CareerBowlingRow,
)

_INTERNATIONAL_FORMATS = frozenset({"Test matches", "One-Day Internationals", "Twenty20 Internationals"})

# Maps page column header text → model field key (matches a field name or validation_alias)
_BATTING_COLUMN_MAP: dict[str, str] = {
    "Mat": "mat",
    "Inns": "inns",
    "NO": "no",
    "Runs": "runs",
    "HS": "hs",
    "Ave": "ave",
    "BF": "bf",
    "SR": "sr",
    "100": "100s",
    "50": "50s",
    "0": "0",
    "4s": "4s",
    "6s": "6s",
}

_BOWLING_COLUMN_MAP: dict[str, str] = {
    "Mat": "mat",
    "Inns": "inns",
    "Overs": "overs",
    "Mdns": "mdns",
    "Runs": "runs",
    "Wkts": "wkts",
    "BBI": "bbi",
    "BBM": "bbm",
    "Ave": "ave",
    "Econ": "econ",
    "SR": "sr",
    "5": "five_w",
    "10": "ten_w",
}

_FIELDING_COLUMN_MAP: dict[str, str] = {
    "Mat": "mat",
    "Inns": "inns",
    "Dis": "dismissals",
    "Ct": "ct",
    "St": "st",
    "Ct Wk": "ct_wk",
    "Ct Fi": "ct_fi",
}


async def get_player_career_stats_from_stats_pages(
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
        batting_html, bowling_html, fielding_html = await asyncio.gather(
            _fetch_stats_page(player_id, "batting", session),
            _fetch_stats_page(player_id, "bowling", session),
            _fetch_stats_page(player_id, "fielding", session),
        )
    finally:
        if owned_session:
            await session.close()

    batting_rows = _parse_batting_career_summary(str(batting_html))
    bowling_rows = _parse_bowling_career_summary(str(bowling_html))
    fielding_rows = _parse_fielding_career_summary(str(fielding_html))

    merged = _merge_batting_and_fielding(batting_rows, fielding_rows)

    return Career(batting_and_fielding=merged, bowling=bowling_rows)


async def _fetch_stats_page(player_id: int, stat_type: str, session: aiohttp.ClientSession) -> str:
    return await get_request(
        route=get_settings().page_routes.player_stats,
        params={"player_id": str(player_id), "stat_type": stat_type},
        base_route=BaseRoute.stats,
        response_output_sub_folder="player_stats",
        session=session,
    )


def _parse_batting_career_summary(html: str) -> list[CareerBattingFieldingRow]:
    """Parse Test/ODI/T20I batting rows from a Statsguru batting stats page."""
    rows = _extract_career_summary_rows(html)
    result = []
    for format_name, cells, headers in rows:
        mapped = _map_cells(headers, cells, _BATTING_COLUMN_MAP)
        mapped["format"] = format_name
        result.append(CareerBattingFieldingRow(**mapped))
    return result


def _parse_bowling_career_summary(html: str) -> list[CareerBowlingRow]:
    """Parse Test/ODI/T20I bowling rows from a Statsguru bowling stats page."""
    rows = _extract_career_summary_rows(html)
    result = []
    for format_name, cells, headers in rows:
        mapped = _map_cells(headers, cells, _BOWLING_COLUMN_MAP)
        mapped["format"] = format_name
        result.append(CareerBowlingRow(**mapped))
    return result


def _parse_fielding_career_summary(html: str) -> list[CareerBattingFieldingRow]:
    """Parse Test/ODI/T20I fielding rows from a Statsguru fielding stats page."""
    rows = _extract_career_summary_rows(html)
    result = []
    for format_name, cells, headers in rows:
        mapped = _map_cells(headers, cells, _FIELDING_COLUMN_MAP)
        mapped["format"] = format_name
        result.append(CareerBattingFieldingRow(**mapped))
    return result


def _merge_batting_and_fielding(
    batting: list[CareerBattingFieldingRow],
    fielding: list[CareerBattingFieldingRow],
) -> list[CareerBattingFieldingRow]:
    """Merge fielding stats into batting rows, matching by format."""
    fielding_by_format = {row.format: row for row in fielding}
    merged = []
    for bat_row in batting:
        fld_row = fielding_by_format.get(bat_row.format)
        if fld_row is None:
            merged.append(bat_row)
            continue

        row_data = bat_row.model_dump()
        row_data.update({
            "catches": fld_row.catches,
            "stumpings": fld_row.stumpings,
            "dismissals": fld_row.dismissals,
            "catches_as_keeper": fld_row.catches_as_keeper,
            "catches_as_fielder": fld_row.catches_as_fielder,
        })
        merged.append(CareerBattingFieldingRow(**row_data))
    return merged


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
        raise ValueError("Could not find 'Career summary' table in stats page")

    table = caption.find_parent("table")

    thead_row = table.find("thead").find("tr")
    headers = [_extract_th_text(th) for th in thead_row.find_all("th")]

    # Only the first <tbody> holds the format-level grouping rows
    first_tbody = table.find("tbody")
    result = []
    for tr in first_tbody.find_all("tr"):
        cells = tr.find_all("td")
        if not cells:
            continue

        b_tag = cells[0].find("b")
        if not b_tag:
            continue

        format_name = b_tag.get_text(strip=True)
        if format_name not in _INTERNATIONAL_FORMATS:
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


def _map_cells(
    headers: list[str],
    cells: list[str],
    column_map: dict[str, str],
) -> dict:
    """
    Zip headers with cell values and produce a dict whose keys match model
    field names or validation aliases, skipping unmapped columns.
    """
    mapped: dict = {}
    for header, value in zip(headers, cells):
        key = column_map.get(header)
        if key and value:
            mapped[key] = value
    return mapped
