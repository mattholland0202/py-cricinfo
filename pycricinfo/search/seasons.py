import re
from pathlib import Path
from urllib.parse import quote, urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from bs4._typing import _OneElement, _QueryResults

from pycricinfo.config import get_settings
from pycricinfo.search.api_helper import format_route
from pycricinfo.source_models.pages.series import MatchSeries, MatchType


def get_matches_in_season(season_name: str | int, fetch: bool = True) -> list[MatchType]:
    """
    Get the Cricinfo web page which lists all series in a given season, and parse out their details.

    Parameters
    ----------
    season_name : str | int
        The name of the season to get matches for, e.g. "2024" or "2020-21"
    fetch : bool, optional
        Whether to fetch the page from the web or use a cached version which already exists at the calculated file
        path, by default True

    Returns
    -------
    list[Series]
        A list of Series, with values for the title, id, link, and summary_url of a series in the season.
    """
    season_name = quote(str(season_name))
    folder = Path(get_settings().api_response_output_folder)
    folder = folder / "seasons"
    folder.mkdir(parents=True, exist_ok=True)
    file_path = (folder / f"{str(season_name)}.html").resolve()

    if fetch:
        session = requests.Session()

        route = format_route(
            get_settings().pages_base_route + get_settings().page_routes.season,
            {"season_name": season_name},
        )

        session.headers["User-Agent"] = get_settings().page_headers.user_agent
        session.headers["Referer"] = urljoin(route, urlparse(route).path)
        session.headers["Accept"] = get_settings().page_headers.accept

        season_page = session.get(route).content

        with open(file_path, "w") as file:
            file.write(str(season_page))

    return parse_season_html(file_path)


def parse_season_html(file_path: Path) -> list[MatchType]:
    """
    Parse the content of the Cricinfo season page HTML file to extract series details.

    Parameters
    ----------
    file_path : Path
        The path to the HTML file containing the season page content.

    Returns
    -------
    list[Series]
        A list of Series, with values for the title, id, link, and summary_url of a series in the season.
    """
    with open(file_path, "r") as file:
        content = file.read()

    content = re.sub(r"^b\'|\'$", "", content)

    soup = BeautifulSoup(content, "html.parser")

    section_heads = soup.find_all("div", class_="match-section-head")

    match_types = []
    for section in section_heads:
        mt = _process_page_section(section)
        if mt:
            match_types.append(mt)

    return match_types


def _process_page_section(section: _OneElement) -> MatchType|None:
    h2_tag = section.find("h2")
    if h2_tag:
        h2_text = h2_tag.text.strip()
        match_type = MatchType(name=h2_text)

        next_section = section.find_next_sibling("section", class_="series-summary-wrap")

        if next_section:
            series_blocks = next_section.find_all("section", class_="series-summary-block collapsed")

            series = _process_series_blocks(series_blocks)
            match_type.series = series
        return match_type


def _process_series_blocks(series_blocks: list[_QueryResults]) -> list[MatchSeries]:
    series_for_type = []
    for block in series_blocks:
        if "data-series-id" not in block.attrs:
            continue

        series_id = block["data-series-id"]

        # Try to find the series name
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
