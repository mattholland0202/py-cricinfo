# pycricinfo

[![PyPI version](https://img.shields.io/pypi/v/pycricinfo)](https://pypi.org/project/pycricinfo/)
[![Upload to PyPi](https://github.com/mattholland0202/py-cricinfo/actions/workflows/python-publish.yml/badge.svg)](https://github.com/mattholland0202/py-cricinfo/actions/workflows/python-publish.yml)
[![Upload to ghcr.io](https://github.com/mattholland0202/py-cricinfo/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/mattholland0202/py-cricinfo/actions/workflows/docker-publish.yml)

A Python package extracting match, player & statistical data from [ESPNCricinfo](https://www.espncricinfo.com), either using their (otherwise undocumented) API, or by scraping pages.

Defines [Pydantic](https://docs.pydantic.dev) models to represent data from the API, allowing easier interaction with the data in your code.

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
This project also comes with an optional dependency to run an API wrapper around Cricinfo, providing an OpenAPI specification through `FastAPI`. Install this optional dependency with:
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
Produces a match scorecard in the CLI, output using [PrettyTable](https://pypi.org/project/prettytable/).  
Can either be from an already downloaded JSON file on disk, or fetched on demand from the API, by changing parameter options:

* `--file`: A path to a JSON file from the Cricinfo match summary API

or

* `--match_id`: The Cricinfo ID of a match while will be fetched from the summary API
* `--series_id`: The Cricinfo ID of the series this match was in

### `print_ballbyball` 
Produces a summary of each ball in a page of data in the CLI.  
Can either be output from an already fetched JSON file on disk, or fetched on demand from the API, by changing parameter options:

* `--file`: A path to a JSON file from the Cricinfo 'play-by-play' API to the

or

* `--match_id`: The Cricinfo ID of a match while will be fetched from the summary API
* `--innings`: The innings of the game to get data from
* `--page`: The page of commentary to return from that innings

----

Installing the optional API dependency adds a further script:

### `run_api`
Runs `uvicorn` to launch a `FastAPI` wrapper around the Cricinfo API, which will launch on port 8000, with the Swagger documentation available at `http://localhost:8000/docs`

## Sample usage: In code
Import one of the `get_` function from the root of the library.

For scorecards as above, use:

```python
from pycricinfo import get_scorecard


async def show_scorecard(series_id: int, match_id: int):
    scorecard = await get_scorecard(series_id, match_id)
    scorecard.show()
```

Other data is available, always returning strongly typed and documented Pydantic models, such as:

```python
from pycricinfo import get_player


async def fetch_player_from_cricinfo(player_id: int):
    cricinfo_player = await get_player(player_id)
    print(cricinfo_player.display_name)
```

### Reusing a session

By default, each call creates and closes its own HTTP session. For better reliability when making multiple requests — particularly when fetching data across several seasons or matches — you can create a shared session using `create_session()` and pass it to each call.

A persistent session retains cookies set by the server across requests, which makes subsequent calls appear more like a real browser session and reduces the likelihood of being rejected with transient 5xx errors.

```python
from pycricinfo import create_session, get_match_types_in_season


async def fetch_multiple_seasons():
    async with create_session() as session:
        season_2023 = await get_match_types_in_season("2023", session=session)
        season_2024 = await get_match_types_in_season("2024", session=session)
        season_2024_25 = await get_match_types_in_season("2024/25", session=session)
```

The session is used as an async context manager, which ensures it is properly closed when done.

## Docker

A docker image is also produced which runs the project's API on port 8000.

Run the included `docker-compose.yml` and browse to `http://localhost:8000/docs` for the Swagger interface.