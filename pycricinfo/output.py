import asyncio
from argparse import ArgumentParser, Namespace

from prettytable import PrettyTable
from pydantic import ValidationError

from pycricinfo.call_cricinfo_api import get_match, get_play_by_play
from pycricinfo.models.output.scorecard import CricinfoScorecard
from pycricinfo.models.source.api.commentary import APIResponseCommentary, Commentary
from pycricinfo.models.source.api.match import Match
from pycricinfo.models.source.pages.player import Career
from pycricinfo.player_stats_pages import get_player_career
from pycricinfo.utils import load_file_and_validate_to_model


def print_scorecard(
    file_path: str = None,
    match_id: int = None,
    series_id: int = None,
    include_batting_minutes: bool = True,
    include_bowling_dots: bool = False,
):
    """
    Prints the scorecard of a match, either by passing a file path or loading from command line arguments

    Parameters
    ----------
    file_path : str, optional
        The path to a JSON file containing match data. If not provided, it will be taken from command line arguments.
    """
    args = parse_scorecard_args()

    if file_path or args.file:
        _print_scorecard_from_file(
            file_path or args.file,
            include_batting_minutes or args.include_batting_minutes,
            include_bowling_dots or args.include_bowling_dots,
        )
    elif match_id or args.match_id:
        _print_scorecard_from_match_id(
            series_id or args.series_id,
            match_id or args.match_id,
            include_batting_minutes or args.include_batting_minutes,
            include_bowling_dots or args.include_bowling_dots,
        )
    else:
        print("Please provide either a file path or match & series IDs")


def _print_scorecard_from_file(
    file_path: str, include_batting_minutes: bool = True, include_bowling_dots: bool = False
):
    model = load_file_and_validate_to_model(file_path, Match)
    _print_scorecard_from_match(model, include_batting_minutes, include_bowling_dots)


def _print_scorecard_from_match_id(
    series_id: int, match_id: int, include_batting_minutes: bool = True, include_bowling_dots: bool = False
):
    model = asyncio.run(get_match(series_id, match_id))
    _print_scorecard_from_match(model, include_batting_minutes, include_bowling_dots)


def _print_scorecard_from_match(match: Match, include_batting_minutes: bool = True, include_bowling_dots: bool = False):
    try:
        sc = CricinfoScorecard(match=match)
        sc.show(include_batting_minutes=include_batting_minutes, include_bowling_dots=include_bowling_dots)
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
    parser.add_argument(
        "--include_batting_minutes", help="Include batting minutes in the scorecard", action="store_true"
    )
    parser.add_argument("--include_bowling_dots", help="Include bowling dots in the scorecard", action="store_true")
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
    model = asyncio.run(get_play_by_play(match_id, innings, page))
    _print_ball_by_ball_from_commentary_model(model)


def _print_ball_by_ball_from_commentary_model(model: Commentary):
    for item in model.deliveries:
        print(f"{item.over.overs}: {item.short_text} - {item.current_innings_score.current_score}")


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


def print_player_career(player_name: str = None, player_id: int = None):
    """
    Print a player's career batting/fielding and bowling stats in a readable table format.

    Parameters
    ----------
    player_name : str, optional
        Player name from the URL slug, for example "Ben Stokes".
    player_id : int, optional
        Cricinfo player ID from the URL.
    """
    args = parse_player_career_args()
    selected_player_name = player_name or args.player_name
    selected_player_id = player_id or args.player_id

    if not selected_player_name or not selected_player_id:
        print("Please provide both --player_name and --player_id")
        return

    career = asyncio.run(get_player_career(player_name=selected_player_name, player_id=selected_player_id))
    _print_player_career_stats(career, selected_player_name)


def _print_player_career_stats(career: Career, player_name: str):
    print(f"\n{player_name} Career Stats")
    print("=" * (len(player_name) + 13))

    batting_table = PrettyTable()
    batting_table.field_names = [
        "Format",
        "Mat",
        "Inns",
        "NO",
        "Runs",
        "HS",
        "Ave",
        "BF",
        "SR",
        "100s",
        "50s",
        "4s",
        "6s",
        "Ct",
        "St",
    ]

    for row in career.batting_and_fielding:
        batting_table.add_row([
            row.format,
            row.matches,
            row.innings,
            row.not_outs,
            row.runs,
            row.highest_score,
            row.average,
            row.balls_faced,
            row.strike_rate,
            row.centuries,
            row.half_centuries,
            row.fours,
            row.sixes,
            row.catches,
            row.stumpings,
        ])

    bowling_table = PrettyTable()
    bowling_table.field_names = [
        "Format",
        "Mat",
        "Inns",
        "Balls",
        "Runs",
        "Wkts",
        "BBI",
        "BBM",
        "Ave",
        "Econ",
        "SR",
        "4w",
        "5w",
        "10w",
    ]

    for row in career.bowling:
        bowling_table.add_row([
            row.format,
            row.matches,
            row.innings,
            row.balls_bowled,
            row.runs_conceded,
            row.wickets,
            row.best_bowling_innings,
            row.best_bowling_match,
            row.average,
            row.economy_rate,
            row.strike_rate,
            row.four_wicket_hauls,
            row.five_wicket_hauls,
            row.ten_wicket_hauls,
        ])

    print("\nBatting & Fielding")
    print(batting_table)
    print("\nBowling")
    print(bowling_table)


def parse_player_career_args() -> Namespace:
    """
    Parse command line arguments for printing a player's career stats.

    Returns
    -------
    argparse.Namespace
        The parsed arguments.
    """
    parser = ArgumentParser()
    parser.add_argument("--player_name", help="Player name from Cricinfo URL, for example 'Ben Stokes'")
    parser.add_argument("--player_id", help="Player ID from Cricinfo URL", type=int)
    args = parser.parse_args()
    return args
