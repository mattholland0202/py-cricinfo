import argparse
import json
from typing import Type, TypeVar

from pydantic import BaseModel, ValidationError

from cricinfo.output_models.scorecard import Scorecard
from cricinfo.source_models.commentary import APIResponseCommentary
from cricinfo.source_models.match import Match

T = TypeVar("T", bound=BaseModel)


def print_scorecard(file_path: str = None):
    if not file_path:
        file_path = parse_args().input
    model = load_file_and_validate_to_model(file_path, Match)
    sc = Scorecard(match=model)
    sc.to_table()


def print_ball_by_ball(file_path: str = None):
    if not file_path:
        file_path = parse_args().input
    model = load_file_and_validate_to_model(file_path, APIResponseCommentary)
    for item in model.commentary.items:
        print(f"{item.over.overs}: {item.short_text} - {item.current_innings_score.score}")

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="Path to the input JSON file", required=True)
    args = parser.parse_args()
    return args

def replace_empty_objects_with_null(data):
    """
    Replace any dictionaries that contain only None values with None

    :param data: The data to check for empty dictionaries
    :return: The data with empty dictionaries replaced with None
    """
    if isinstance(data, dict):
        if all(value is None for value in data.values()):
            return None
        return {key: replace_empty_objects_with_null(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [replace_empty_objects_with_null(item) for item in data]
    else:
        return data 

def load_file_and_validate_to_model(file_path: str, type_to_parse: Type[T]) -> T:
    with open(file_path, "r") as content:
        json_data = json.load(content)
        modified_data = replace_empty_objects_with_null(json_data)
        try:
            model = type_to_parse.model_validate(modified_data)
        except ValidationError as ex:
            print(ex)
            exit(1)

    return model