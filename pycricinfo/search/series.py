import re

from bs4 import BeautifulSoup

from pycricinfo.config import BaseRoute, get_settings
from pycricinfo.cricinfo.api_helper import get_request
from pycricinfo.source_models.pages.series import MatchResult


def _clean_text(text: str) -> str:
    """
    Remove line breaks, extra spaces and normalise whitespace

    Parameters
    ----------
    text : str
        The text to clean

    Returns
    -------
    str
        The cleaned text
    """
    if not text:
        return ""
    text = text.replace("\\n", "")
    return re.sub(r"\s+", " ", text).strip()


def extract_match_ids_from_series(series_id: int | str) -> list[MatchResult]:
    """
    Extract match IDs from a series by fetching the series page and parsing the matches.

    Parameters
    ----------
    series_id : int | str
        The ID of the series to extract match IDs from.

    Returns
    -------
    list[MatchResult]
        A list of match results extracted from the series.
    """
    content = get_request(
        route=get_settings().page_routes.matches_in_series,
        params={"series_id": series_id},
        base_route=BaseRoute.page,
        response_output_sub_folder="series",
    )

    soup = BeautifulSoup(content, "html.parser")
    matches: list[MatchResult] = []

    match_blocks = soup.find_all("section", class_="default-match-block")

    for match in match_blocks:
        match_result_data = {}

        match_link = match.select_one(".match-no a")
        if match_link:
            href = match_link.get("href", "")
            scorecard_match = re.search(r"/scorecard/(\d+)/", href)
            if scorecard_match:
                match_result_data["id"] = scorecard_match.group(1)

            match_result_data["description"] = _clean_text(match_link.get_text())

        innings1 = match.find("div", class_="innings-info-1")
        if innings1:
            match_result_data["innings_1_info"] = _clean_text(innings1.get_text())

        innings2 = match.find("div", class_="innings-info-2")
        if innings2:
            match_result_data["innings_2_info"] = _clean_text(innings2.get_text())

        status = match.find("div", class_="match-status")
        if status:
            match_result_data["status"] = _clean_text(status.get_text())

        if "id" in match_result_data:
            matches.append(MatchResult(**match_result_data))

    return matches
