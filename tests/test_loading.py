import os

import pytest

from pycricinfo.source_models.api.match import Match
from pycricinfo.source_models.api.match_basic import MatchBasic
from pycricinfo.utils import load_file_and_validate_to_model


def get_test_file_path(file_name: str) -> str:
    """Get the full path to a test file."""
    return os.path.join(os.path.dirname(__file__), "test_files", file_name)


@pytest.mark.parametrize("file_name", ["match/1426555.json", "match/1243385.json", "match/1381212.json"])
def test_load_match(file_name):
    """Test loading JSON files into Match model without exceptions."""
    test_file_path = get_test_file_path(file_name)

    result = load_file_and_validate_to_model(test_file_path, Match)

    assert result is not None
    assert isinstance(result, Match)


def test_load_match_basic():
    """Test loading JSON files into MatchBasic model without exceptions."""
    test_file_path = get_test_file_path("match_basic/1225249_basic.json")

    result = load_file_and_validate_to_model(test_file_path, MatchBasic)

    assert result is not None
    assert isinstance(result, MatchBasic)
