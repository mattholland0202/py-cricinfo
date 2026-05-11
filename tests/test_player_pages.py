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
            7216,
            MatchTypeNames.TESTS,
            245,
        ),
        (
            "tests/test_files/player/578769_page.html",
            MatchTypeNames.FIRST_CLASS,
            6272,
            MatchTypeNames.FIRST_CLASS,
            349,
        ),
        (
            "tests/test_files/player/297074_page.html",
            MatchTypeNames.WOMENS_TESTS,
            612,
            MatchTypeNames.WOMENS_TESTS,
            None,
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


def test_parse_player_career_stats_page_all_fields_for_311158():
    with open("tests/test_files/player/311158_page.html", "r") as player_page:
        content = player_page.read()

    career = _parse_player_career_stats_page(content)

    assert isinstance(career, Career)
    assert len(career.batting_and_fielding) > 0
    assert len(career.bowling) > 0

    test_batting = next(row for row in career.batting_and_fielding if row.format == MatchTypeNames.TESTS)
    assert test_batting.format == MatchTypeNames.TESTS
    assert test_batting.matches == 120
    assert test_batting.innings == 216
    assert test_batting.not_outs == 9
    assert test_batting.runs == 7216
    assert test_batting.highest_score == "258"
    assert test_batting.average == 34.85
    assert test_batting.balls_faced == 12348
    assert test_batting.strike_rate == 58.43
    assert test_batting.centuries == 14
    assert test_batting.half_centuries == 37
    assert test_batting.fours == 828
    assert test_batting.sixes == 136
    assert test_batting.catches == 115
    assert test_batting.stumpings == 0

    test_bowling = next(row for row in career.bowling if row.format == MatchTypeNames.TESTS)
    assert test_bowling.format == MatchTypeNames.TESTS
    assert test_bowling.matches == 120
    assert test_bowling.innings == 178
    assert test_bowling.balls_bowled == 13767
    assert test_bowling.runs_conceded == 7655
    assert test_bowling.wickets == 245
    assert test_bowling.best_bowling_innings == "6/22"
    assert test_bowling.best_bowling_match == "8/161"
    assert test_bowling.average == 31.24
    assert test_bowling.economy_rate == 3.33
    assert test_bowling.strike_rate == 56.1
    assert test_bowling.four_wicket_hauls == 9
    assert test_bowling.five_wicket_hauls == 6
    assert test_bowling.ten_wicket_hauls == 0
