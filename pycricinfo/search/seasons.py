import re

from bs4 import BeautifulSoup
from bs4._typing import _OneElement, _QueryResults

from pycricinfo.config import BaseRoute, get_settings
from pycricinfo.search.api_helper import get_request
from pycricinfo.source_models.pages.series import MatchSeries, MatchType


def get_match_types_in_season(season_name: str | int) -> list[MatchType]:
    """
    Get the Cricinfo web page which lists all series in a given season, and parse out their details.

    Parameters
    ----------
    season_name : str | int
        The name of the season to get matches for, e.g. "2024" or "2020-21"

    Returns
    -------
    list[MatchType]
        A list of match types, each containing a list of series in that match type for this season.
    """
    content = get_request(
        route=get_settings().page_routes.series_in_season,
        params={"season_name": season_name},
        base_route=BaseRoute.page,
        response_output_sub_folder="seasons",
    )

    return parse_season_html(content)


def parse_season_html(content: str) -> list[MatchType]:
    """
    Parse the content of the Cricinfo season page HTML file to extract series details.

    Parameters
    ----------
    content : str
        The season page content.

    Returns
    -------
    list[Series]
        A list of Series, with values for the title, id, link, and summary_url of a series in the season.
    """
    content = re.sub(r"^b\'|\'$", "", content)

    soup = BeautifulSoup(content, "html.parser")

    section_heads = soup.find_all("div", class_="match-section-head")

    match_types = []
    for section in section_heads:
        mt = _process_match_type_page_section(section)
        if mt:
            match_types.append(mt)

    return match_types


def _process_match_type_page_section(section: _OneElement) -> MatchType | None:
    """
    Each page section representing a type of match should contian a h2 tag with the match type name,
    and then the following section will be a list of series of that type within the season

    Parameters
    ----------
    section : _OneElement
        The section of the series page for this match type

    Returns
    -------
    MatchType | None
        If the correct data was present, a parsed MatchType object, otherwise None
    """
    h2_tag = section.find("h2")
    if not h2_tag:
        return

    h2_text = h2_tag.text.strip()
    match_type = MatchType(name=h2_text)

    next_section = section.find_next_sibling("section", class_="series-summary-wrap")

    if next_section:
        series_blocks = next_section.find_all("section", class_="series-summary-block collapsed")

        series = _process_series_blocks(series_blocks)
        match_type.series = series
    return match_type


def _process_series_blocks(series_blocks: list[_QueryResults]) -> list[MatchSeries]:
    """
    Process all sections matched by BeautifulSoup which have the classes representing series within a match type.
    Iterate over the blocks and, within each, find the data for the series_id, title, and useful links.

    Parameters
    ----------
    series_blocks : list[_QueryResults]
        A list of blocks of data representing series in the match type

    Returns
    -------
    list[MatchSeries]
        A list of parsed series of matches
    """
    series_for_type = []
    for block in series_blocks:
        if "data-series-id" not in block.attrs:
            continue

        series_id = block["data-series-id"]

        series_link = block.find("a")
        if series_link:
            title = series_link.contents[0]
            title = re.sub(r"\\", "", title)
            title = re.sub(r"\s{2,}|\n|\r", " ", title).strip()

            series_id = block.get("data-series-id")
            summary_url = block.get("data-summary-url")

            link = series_link.get("href", "")
            s = MatchSeries(title=title, id=series_id, link=link, summary_url=summary_url)
            series_for_type.append(s)
    return series_for_type
