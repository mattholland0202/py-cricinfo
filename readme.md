# pycricinfo

[![PyPI version](https://img.shields.io/pypi/v/pycricinfo)](https://pypi.org/project/pycricinfo/)
[![Upload to PyPi](https://github.com/mattholland0202/py-cricinfo/actions/workflows/python-publish.yml/badge.svg)](https://github.com/mattholland0202/py-cricinfo/actions/workflows/python-publish.yml)

A Python package using ESPNCricinfo's API to extract match, player & statistical data.

Defines Pydantic models to represent data from the Cricinfo API, allowing easier interaction with the data in your code.

## Project status
:warning: This project is still in pre-release and, whilst it still has a `0.0.X` version number, is liable to change in a breaking way with any release :warning:

## Installation
Use your package manager of choice to install `pycricinfo`. For example:

#### Pip
```
pip install pycricinfo
```

#### UV
```
uv add pycricinfo
```

### Optional installation: API
This project also comes with an optional dependency to run an API wrapper around Cricinfo, providing an OpenAPI specification via Swagger through `FastAPI`. Install this optional dependency with:
```
pip install 'pycricinfo[api]'
```
or
```
uv add pycricinfo --optional api
```

## Sample usage: CLI
Installing the project adds 2 scripts:

### `print_scorecard`
Produces a match scorecard in the CLI.

Parameters:
* `--file`: A path to a JSON file from the Cricinfo match summary API
* `--match_id`: The Cricinfo ID of a match while will be fetched from the summary API
### `print_ballbyball` 
Produces a summary of each ball in a page of data in the CLI.

Parameters:
* `--file`: A path to a JSON file from the Cricinfo 'play-by-play' API to the
* `--match_id`: The Cricinfo ID of a match while will be fetched from the summary API
* `--innings`: The innings of the game to get data from
* `--page`: The page of commentary to return from that innings


Installing the optional API dependency adds a further script:

### `run_api`
Runs `uvicorn` to launch a `FastAPI` wrapper around the Cricinfo API, which will launch on port 8000, with the Swagger documentation available at `http://localhost:8000/docs`

## Sample usage: In code
Import one of the `get_` function from `pycricinfo.search`, for example:
```python
from pycricinfo.search import get_player


def fetch_player_from_cricinfo(player_id: int):
    cricinfo_player = get_player(player_id)
    print(cricinfo_player.display_name)
```