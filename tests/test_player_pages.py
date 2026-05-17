from pycricinfo.player_stats_pages import (
    _merge_batting_and_fielding,
    _parse_batting_career_summary,
    _parse_bowling_career_summary,
    _parse_fielding_career_summary,
)
from pycricinfo.types.match_types import MatchTypeNames

# ---------------------------------------------------------------------------
# Stats-page parser tests (stats.espncricinfo.com format)
# ---------------------------------------------------------------------------

BATTING_FILE = "tests/test_files/player/31158_stats_page_batting_all.html"
BOWLING_FILE = "tests/test_files/player/31158_stats_page_bowling_all.html"
FIELDING_FILE = "tests/test_files/player/31158_stats_page_fielding_all.html"


def _read(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def test_parse_stats_batting_career_summary():
    rows = _parse_batting_career_summary(_read(BATTING_FILE))

    assert len(rows) == 3
    assert {r.format for r in rows} == {MatchTypeNames.TESTS, MatchTypeNames.ODIs, MatchTypeNames.T20Is}

    test = next(r for r in rows if r.format == MatchTypeNames.TESTS)
    assert test.matches == 120
    assert test.innings == 216
    assert test.not_outs == 9
    assert test.runs == 7216
    assert test.highest_score == "258"
    assert test.average == 34.85
    assert test.balls_faced == 12348
    assert test.strike_rate == 58.43
    assert test.centuries == 14
    assert test.half_centuries == 37
    assert test.ducks == 17
    assert test.fours == 828
    assert test.sixes == 136

    odi = next(r for r in rows if r.format == MatchTypeNames.ODIs)
    assert odi.matches == 114
    assert odi.runs == 3463

    t20i = next(r for r in rows if r.format == MatchTypeNames.T20Is)
    assert t20i.matches == 43
    assert t20i.runs == 585
    assert t20i.highest_score == "52*"


def test_parse_stats_bowling_career_summary():
    rows = _parse_bowling_career_summary(_read(BOWLING_FILE))

    assert len(rows) == 3
    assert {r.format for r in rows} == {MatchTypeNames.TESTS, MatchTypeNames.ODIs, MatchTypeNames.T20Is}

    test = next(r for r in rows if r.format == MatchTypeNames.TESTS)
    assert test.matches == 120
    assert test.innings == 178
    assert test.overs == "2294.3"
    assert test.maidens == 391
    assert test.runs_conceded == 7655
    assert test.wickets == 245
    assert test.best_bowling_innings == "6/22"
    assert test.best_bowling_match == "8/161"
    assert test.average == 31.24
    assert test.economy_rate == 3.33
    assert test.strike_rate == 56.1
    assert test.five_wicket_hauls == 6
    assert test.ten_wicket_hauls == 0

    odi = next(r for r in rows if r.format == MatchTypeNames.ODIs)
    assert odi.wickets == 74
    assert odi.five_wicket_hauls == 1


def test_parse_stats_fielding_career_summary():
    rows = _parse_fielding_career_summary(_read(FIELDING_FILE))

    assert len(rows) == 3
    assert {r.format for r in rows} == {MatchTypeNames.TESTS, MatchTypeNames.ODIs, MatchTypeNames.T20Is}

    test = next(r for r in rows if r.format == MatchTypeNames.TESTS)
    assert test.catches == 115
    assert test.stumpings == 0
    assert test.dismissals == 115
    assert test.catches_as_keeper == 0
    assert test.catches_as_fielder == 115


def test_merge_batting_and_fielding_combines_all_fields():
    batting_rows = _parse_batting_career_summary(_read(BATTING_FILE))
    fielding_rows = _parse_fielding_career_summary(_read(FIELDING_FILE))
    merged = _merge_batting_and_fielding(batting_rows, fielding_rows)

    assert len(merged) == 3

    test = next(r for r in merged if r.format == MatchTypeNames.TESTS)
    # Batting fields preserved
    assert test.runs == 7216
    assert test.centuries == 14
    # Fielding fields merged in
    assert test.catches == 115
    assert test.stumpings == 0
    assert test.dismissals == 115
    assert test.catches_as_fielder == 115
