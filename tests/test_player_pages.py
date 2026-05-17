import pytest

from pycricinfo.models.source.pages.player import CareerBattingFieldingRow
from pycricinfo.player_stats_pages import _parse_career_summary_rows
from pycricinfo.types.match_types import MatchTypeNames

# ---------------------------------------------------------------------------
# Stats-page parser tests (stats.espncricinfo.com format)
# ---------------------------------------------------------------------------


PLAYER_CASES = [
    {
        "name": "all_formats",
        "batting": "tests/test_files/player/31158_stats_page_batting_all.html",
        "bowling": "tests/test_files/player/31158_stats_page_bowling_all.html",
        "fielding": "tests/test_files/player/31158_stats_page_fielding_all.html",
        "expected": {
            MatchTypeNames.TESTS: {"matches": 120, "runs": 7216},
            MatchTypeNames.ODIs: {"matches": 114, "runs": 3463},
            MatchTypeNames.T20Is: {"matches": 43, "runs": 585},
        },
    },
    {
        "name": "no_formats",
        "batting": "tests/test_files/player/578769_stats_page_batting_all.html",
        "bowling": None,
        "fielding": None,
        "expected": {
            MatchTypeNames.TESTS: None,
            MatchTypeNames.ODIs: None,
            MatchTypeNames.T20Is: None,
        },
    },
    {
        "name": "partial_formats",
        "batting": "tests/test_files/player/464626_stats_page_batting_all.html",
        "bowling": None,
        "fielding": None,
        "expected": {
            MatchTypeNames.TESTS: {"matches": 8, "runs": 182},
            MatchTypeNames.ODIs: {"matches": 7, "runs": 68},
            MatchTypeNames.T20Is: None,
        },
    },
]


def _read(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


@pytest.mark.parametrize("case", PLAYER_CASES, ids=[c["name"] for c in PLAYER_CASES])
def test_parse_stats_batting_career_summary(case):
    rows = _parse_career_summary_rows(_read(case["batting"]), CareerBattingFieldingRow)
    present_formats = {fmt for fmt, expected in case["expected"].items() if expected is not None}
    row_formats = {r.format for r in rows}
    assert row_formats == present_formats
    for fmt, expected in case["expected"].items():
        if expected is None:
            # Should not be present in the output
            assert fmt not in row_formats
        else:
            row = next(r for r in rows if r.format == fmt)
            for k, v in expected.items():
                assert getattr(row, k) == v
