from argparse import ArgumentParser, Namespace

from pydantic import ValidationError

from pycricinfo.call_cricinfo_api import get_match, get_play_by_play
from pycricinfo.models.output.scorecard import CricinfoScorecard
from pycricinfo.models.source.api.commentary import APIResponseCommentary, Commentary
from pycricinfo.models.source.api.match import Match
from pycricinfo.utils import load_file_and_validate_to_model


def print_scorecard(file_path: str = None, match_id: int = None, series_id: int = None):
    """
    Prints the scorecard of a match, either by passing a file path or loading from command line arguments

    Parameters
    ----------
    file_path : str, optional
        The path to a JSON file containing match data. If not provided, it will be taken from command line arguments.
    """
    args = parse_scorecard_args()

    if file_path or args.file:
        _print_scorecard_from_file(file_path or args.file)
    elif match_id or args.match_id:
        _print_scorecard_from_match_id(series_id or args.series_id, match_id or args.match_id)
    else:
        print("Please provide either a file path or match & series IDs")


def _print_scorecard_from_file(file_path: str):
    model = load_file_and_validate_to_model(file_path, Match)
    _print_scorecard_from_match(model)


def _print_scorecard_from_match_id(series_id: int, match_id: int):
    model = get_match(series_id, match_id)
    _print_scorecard_from_match(model)


def _print_scorecard_from_match(match: Match):
    try:
        sc = CricinfoScorecard(match=match)
        sc.show(include_batting_minutes=False, include_bowling_dots=False)
    except ValidationError as validation_error:
        print(validation_error.errors())
        raise


def parse_scorecard_args() -> Namespace:
    """
    Parse command line arguments

    Returns
    -------
    argparse.Namespace
        The parsed arguments
    """
    parser = ArgumentParser()
    parser.add_argument("--file", help="Path to a JSON file to parse and print from")
    parser.add_argument("--series_id", help="ID of the series of the match to fetch from the API")
    parser.add_argument("--match_id", help="ID of the match to fetch from the API")
    args = parser.parse_args()
    return args


def print_ball_by_ball(file_path: str = None, match_id: int = None, innings: int = 1, page: int = 1):
    """
    Prints a page of ball by ball commentary of a match, either by passing a file path or loading from command line
    arguments

    Parameters
    ----------
    file_path : str, optional
        The path to a JSON file containing match data. If not provided, it will be taken from command line arguments.
    match_id : int, optional
        The ID of the match to fetch from the API. If not provided, it will be taken from command line arguments.
    innings : int, optional
        The innings of the match to fetch commentary for. Defaults to 1.
    page : int, optional
        The page of commentary to fetch. Defaults to 1.
    """
    args = parse_ball_by_ball_args()

    if file_path or args.file:
        _print_ball_by_ball_from_file(file_path or args.file)
    elif match_id or args.match_id:
        match_id = match_id or args.match_id
        innings = innings or args.innings
        page = page or args.page
        _print_ball_by_ball_from_match_id(match_id, innings, page)
    else:
        print("Please provide either a file path or match ID and innings/page parameters.")


def _print_ball_by_ball_from_file(file_path: str):
    model = load_file_and_validate_to_model(file_path, APIResponseCommentary)
    _print_ball_by_ball_from_commentary_model(model.commentary)


def _print_ball_by_ball_from_match_id(match_id: int, innings: int, page: int):
    model = get_play_by_play(match_id, innings, page)
    _print_ball_by_ball_from_commentary_model(model)


def _print_ball_by_ball_from_commentary_model(model: Commentary):
    for item in model.deliveries:
        print(f"{item.over.overs}: {item.short_text} - {item.current_innings_score.score}")


def parse_ball_by_ball_args() -> Namespace:
    """
    Parse command line arguments

    Returns
    -------
    argparse.Namespace
        The parsed arguments
    """
    parser = ArgumentParser()
    parser.add_argument("--file", help="Path to a JSON file to parse and print from")
    parser.add_argument("--match_id", help="ID of the match to fetch from the API")
    parser.add_argument("--innings", help="The innings of the game to get data from", type=int, default=1)
    parser.add_argument("--page", help="The page of commentary to return from that innings", type=int, default=1)
    args = parser.parse_args()
    return args
