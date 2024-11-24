import argparse
import json

from pydantic import ValidationError

from cricinfo.output_models.scorecard import Scorecard
from cricinfo.source_models.match import Match


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="Path to the input JSON file", required=True)
    args = parser.parse_args()
    output(args.input)

def output(file_path: str):
    with open(file_path, "r") as content:
        summary = json.load(content)
        try:
            match = Match.model_validate(summary)
        except ValidationError as ex:
            print(ex)
            exit(1)

    sc = Scorecard(match=match)
    sc.to_table()