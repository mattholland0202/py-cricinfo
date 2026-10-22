"""Tests that saved API responses validate against the source models."""

from pathlib import Path

import pytest

from pycricinfo.models.source import Match, MatchBasic, MatchCompetitorBasic
from pycricinfo.models.source.api.commentary import APIResponseCommentary
from pycricinfo.models.source.api.player import Player
from pycricinfo.utils import load_file_and_validate_to_model


def get_test_file_path(file_name: str) -> str:
    """Get the full path to a test file."""
    return str(Path(__file__).parent / "test_files" / file_name)


@pytest.mark.parametrize("file_name", ["match/1426555.json", "match/1243385.json", "match/1381212.json"])
def test_load_match(file_name: str) -> None:
    """Test loading JSON files into Match model without exceptions."""
    test_file_path = get_test_file_path(file_name)

    result = load_file_and_validate_to_model(test_file_path, Match)

    assert result is not None
    assert isinstance(result, Match)


def test_load_match_basic() -> None:
    """Test loading JSON files into MatchBasic model without exceptions."""
    test_file_path = get_test_file_path("match_basic/1225249_basic.json")

    result = load_file_and_validate_to_model(test_file_path, MatchBasic)

    assert result is not None
    assert isinstance(result, MatchBasic)


def test_load_match_team() -> None:
    """Test loading JSON files into MatchCompetitorBasic model without exceptions."""
    test_file_path = get_test_file_path("match_team/1381212_4.json")

    result = load_file_and_validate_to_model(test_file_path, MatchCompetitorBasic)

    assert result is not None
    assert isinstance(result, MatchCompetitorBasic)


@pytest.mark.parametrize("file_name", ["ball_by_ball/1031439_1_1.json", "ball_by_ball/1031439_1_3.json"])
def test_load_ball_by_ball_page(file_name: str) -> None:
    """Test loading JSON files into APIResponseCommentary model without exceptions."""
    test_file_path = get_test_file_path(file_name)

    result = load_file_and_validate_to_model(test_file_path, APIResponseCommentary)

    assert result is not None
    assert isinstance(result, APIResponseCommentary)


def test_load_plater() -> None:
    """Test loading JSON files into Player model without exceptions."""
    test_file_path = get_test_file_path("player/303669.json")

    result = load_file_and_validate_to_model(test_file_path, Player)

    assert result is not None
    assert isinstance(result, Player)
