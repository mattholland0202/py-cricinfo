# AGENTS.md

Guidance for AI coding agents working on `pycricinfo`, a Python package that fetches match, player and statistical data
from ESPNCricinfo. It uses Cricinfo's undocumented JSON APIs and scrapes HTML pages, and parses the results into
Pydantic models.

## Setup and commands

The project uses [uv](https://docs.astral.sh/uv/) and requires Python 3.13+.

```sh
uv sync --all-extras --dev          # install everything, including the optional FastAPI extra
uv run pytest tests/                # run tests (offline, against fixtures in tests/test_files)
uv run ruff check .                 # lint
uv run ruff format .                # format
git config core.hooksPath .githooks # enable the pre-push hook (ruff check + pytest)
```

CI (`.github/workflows/python-publish.yml`) runs `uv sync --locked`, `ruff check` and `pytest`, so `uv.lock` must be
kept in sync with `pyproject.toml`. Run `uv lock` after changing dependencies.

## Code style

- Ruff, line length 120, double quotes, rules `E`, `F`, `I`, `W`. `pycricinfo` is first-party for import sorting.
- Docstrings use the numpy format (`Parameters`, `Returns`, `Raises` sections with `----------` underlines). Public
  functions and model validators are expected to have them.
- Type hints are used throughout. Fields that default to `None` must be typed `Optional[...]`.
- Public functions that make HTTP requests are `async` and accept an optional `session: aiohttp.ClientSession`. If
  none is passed, they create and close their own. Keep this pattern for new fetch functions.

## Layout

```
pycricinfo/
  __init__.py             Public API: re-exports get_* functions, create_session, output models and types
  config.py               Settings (pydantic-settings): base URLs, route templates, headers, match classes
  api_helper.py           HTTP layer: get_request / get_and_parse, session creation, bot-protection handling
  call_cricinfo_api.py    get_player, get_team, get_match, get_scorecard, get_play_by_play, etc.
  player_stats_pages.py   get_player_career: scrapes Statsguru batting/bowling/fielding pages (men's players only)
  search/                 Scrapes season and series listing pages
  output.py               CLI entry points (print_scorecard, print_ballbyball)
  utils.py                JSON loading/validation helpers, package metadata lookup
  exceptions.py           CricinfoAPIException (status code, route, content)
  types/match_types.py    Enums: MatchTypeNames, MatchNoteType (aenum MultiValueEnum), DeliveryPlayTypes
  models/source/api/      Pydantic models mirroring Cricinfo API responses
  models/source/pages/    Pydantic models for data scraped from HTML pages
  models/output/          Derived models built from source models (Scorecard, Innings, batting/bowling rows)
  api/                    Optional FastAPI app (server.py) and routers (endpoints/)
tests/
  test_loading.py         Validates JSON fixtures against source models
  test_player_pages.py    Statsguru HTML parsing against fixture pages
  test_files/             Saved API responses (JSON) and pages (HTML) used as fixtures
```

## How requests work

- Route templates live in `config.py` (`CoreAPIRoutes`, `PageRoutes`) and use `{placeholder}` syntax. They are
  filled by `_format_route` in `api_helper.py`. Placeholders that aren't supplied are left in the URL as-is, so make
  sure every placeholder in a template is passed.
- `BaseRoute` selects the host:
  - `core`: `core.espnuk.org/v2/sports/cricket/` (JSON)
  - `site`: `site.api.espn.com/apis/site/v2/sports/cricket/` (JSON; match summary and play-by-play)
  - `page`: `www.espncricinfo.com` (HTML)
  - `stats`: `stats.espncricinfo.com` (HTML; Statsguru)
- HTML routes (`page`, `stats`) detect Akamai bot-protection pages. When blocked, they retry once with `curl_cffi`
  impersonating a Firefox TLS fingerprint. The impersonation target should stay consistent with the User-Agent in
  `PageHeaders` (`config.py`).
- Any non-200 status raises `CricinfoAPIException`. The FastAPI app turns it into a JSON response with that status
  code.
- **Side effect:** `get_request` writes every response to `responses/<sub_folder>/<YYYYMMDD>/` (configurable via
  `api_response_output_folder`). That folder is gitignored. Never commit it.

## Models

- Source API models extend `CCBaseModel` (`models/source/api/common.py`). It generates camelCase validation aliases,
  so fields are declared in snake_case and validate from the camelCase JSON. It also turns empty-dict values into
  `None`.
- Cricinfo often returns `{}` or other falsy values instead of `null`. Use `LeniantOptional[...]` (spelling is
  intentional, it's an existing name) for fields that do this, or `replace_empty_objects_with_null`.
- Use `AliasChoices` when a field has several source names (e.g. `batter`/`batsman`, `innings`/`linescores`).
- Statistics are lists of `{name, value}` pairs. Look them up with `.find("statName")` on innings/statistics
  containers. Player innings can also look up `"batting.<attr>"` / `"bowling.<attr>"` on the extended details.
- `@computed_field` return annotations must match the actual returned type, otherwise Pydantic emits serializer
  warnings on `model_dump`.
- Output models (`models/output/`) are built in `model_validator(mode="before")` hooks that transform source models.
  For example, `CricinfoScorecard(match=match)` builds innings from `match.header` and fills batters/bowlers from
  `match.rosters`, keyed by innings number (`period`).
- Statsguru career rows (`models/source/pages/player.py`) use validation aliases that must exactly match the HTML
  table headers (e.g. `"Mat"`, `"HS"`, `"Ct Wk"`). `"-"` cells are normalised to `None`.

## Testing

- Tests run offline and must not hit the network. To test new parsing, save a real response into
  `tests/test_files/<category>/` (named by ID, e.g. `match/1426555.json` or
  `player/<id>_stats_page_<type>_all.html`) and add it to the parametrized cases.
- `load_file_and_validate_to_model(path, Model)` in `utils.py` loads a fixture and raises `ValidationError` on
  mismatch. The CLI wraps it to print the error and exit 1.
- Model changes should be checked against every fixture in `tests/test_files`. Cricinfo data varies a lot between
  formats (Tests vs limited overs, men's vs women's, old vs recent matches).

## Releases and versioning

- Each release bumps `version` in `pyproject.toml` and adds a section to `changelog.md` (Keep a Changelog format:
  `### Fixed`, `### Changed`, `### Added`). Add changelog entries for user-facing changes.
- Publishing a GitHub release triggers `python-publish.yml` (lint, test, build, publish to PyPI). On success,
  `docker-publish.yml` builds and pushes `ghcr.io/mattholland0202/py-cricinfo` tagged with the version and `latest`.
- The API runs on port 8000 (`Settings.port`), both via the `run_api` script and in the Docker image. Running
  `uv run python -m pycricinfo.api.server` starts it with auto-reload for development.
- Don't commit, push, tag or publish unless asked.
