import pytest

from pycricinfo.models.source.pages.player import Career
from pycricinfo.player_pages import _parse_player_career_stats_page
from pycricinfo.types.match_types import MatchTypeNames


@pytest.mark.parametrize(
    "file,expected_batting_format,expected_runs,expected_bowling_format,expected_wickets",
    [
        (
            "tests/test_files/player/311158_page.html",
            MatchTypeNames.TESTS,
            "7216",
            MatchTypeNames.TESTS,
            "245",
        ),
        (
            "tests/test_files/player/578769_page.html",
            MatchTypeNames.FIRST_CLASS,
            "6272",
            MatchTypeNames.FIRST_CLASS,
            "349",
        ),
        (
            "tests/test_files/player/297074_page.html",
            MatchTypeNames.WOMENS_TESTS,
            "612",
            MatchTypeNames.WOMENS_TESTS,
            "-",
        ),
    ],
)
def test_parse_player_career_stats_page(
    file, expected_batting_format, expected_runs, expected_bowling_format, expected_wickets
):
    with open(file, "r") as player_page:
        content = player_page.read()

    career = _parse_player_career_stats_page(content)

    assert isinstance(career, Career)
    assert len(career.batting_and_fielding) > 0
    assert len(career.bowling) > 0

    assert isinstance(career.batting_and_fielding[0].format, MatchTypeNames)
    assert isinstance(career.bowling[0].format, MatchTypeNames)
    assert career.batting_and_fielding[0].format == expected_batting_format
    assert career.batting_and_fielding[0].runs == expected_runs
    assert career.bowling[0].format == expected_bowling_format
    assert career.bowling[0].wickets == expected_wickets
