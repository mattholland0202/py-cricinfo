# pycricinfo

A Python package using ESPNCricinfo's API to extract match, player & statistical data.

Defines Pydantic models to represent data from the Cricinfo API, allowing easier interaction with the data in your code.

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

* `scorecard`: Pass a JSON file from the Cricinfo match summary API to the `--input` parameter to produce a scorecard in the CLI
* `ballbyball`: Pass a JSON file from the Cricinfo 'play-by-play' API to the `--input` parameter to produce a sumary of each ball in the page of data in the CLI

Installing the optional API dependency adds a further script:

* `api`: Runs `uvicorn` to launch a `FastAPI` wrapper around the Cricinfo API, which will launch on port 8000, with the Swagger documentation available at `http://localhost:8000/docs`