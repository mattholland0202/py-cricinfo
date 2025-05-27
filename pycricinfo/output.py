import argparse

from pycricinfo.output_models.scorecard import Scorecard
from pycricinfo.source_models.commentary import APIResponseCommentary
from pycricinfo.source_models.match import Match
from pycricinfo.utils import load_file_and_validate_to_model


def print_scorecard(file_path: str = None):
    """
    Prints the scorecard of a match, either by passing a file path or loading from command line arguments

    Parameters
    ----------
    file_path : str, optional
        The path to a JSON file containing match data. If not provided, it will be taken from command line arguments.
    """
    if not file_path:
        file_path = parse_args().input
    model = load_file_and_validate_to_model(file_path, Match)
    sc = Scorecard(match=model)
    sc.to_table()


def print_ball_by_ball(file_path: str = None):
    """
    Prints a page of ball by ball commentary of a match, either by passing a file path or loading from command line
    arguments

    Parameters
    ----------
    file_path : str, optional
        The path to a JSON file containing match data. If not provided, it will be taken from command line arguments.
    """
    if not file_path:
        file_path = parse_args().input
    model = load_file_and_validate_to_model(file_path, APIResponseCommentary)
    for item in model.commentary.items:
        print(f"{item.over.overs}: {item.short_text} - {item.current_innings_score.score}")


def parse_args():
    """
    Parse command line arguments

    Returns
    -------
    The parsed arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="Path to the input JSON file", required=True)
    args = parser.parse_args()
    return args
