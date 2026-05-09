import pytest

from pycricinfo.models.source.pages.player import Career
from pycricinfo.player_pages import parse_player_career_stats_page


@pytest.mark.parametrize(
    "file,expected_batting_format,expected_runs,expected_bowling_format,expected_wickets",
    [
        ("tests/test_files/player/311158_page.html", "Tests", "7216", "Tests", "245"),
        ("tests/test_files/player/578769_page.html", "FC", "6272", "FC", "349"),
    ],
)
def test_parse_player_career_stats_page(
    file, expected_batting_format, expected_runs, expected_bowling_format, expected_wickets
):
    with open(file, "r") as player_page:
        content = player_page.read()

    career = parse_player_career_stats_page(content)

    assert isinstance(career, Career)
    assert len(career.batting_and_fielding) > 0
    assert len(career.bowling) > 0

    assert career.batting_and_fielding[0].format == expected_batting_format
    assert career.batting_and_fielding[0].runs == expected_runs
    assert career.bowling[0].format == expected_bowling_format
    assert career.bowling[0].wickets == expected_wickets
