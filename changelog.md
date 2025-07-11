# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.14]
### Added
- Extract extra fields to make a fuller scorecard

## [0.0.13]
### Added
- Match Note types as an enum
- Parse partnership and fall of wicket data in Match
- Overs to Scorecard output
- CLI parameters to fetch match from API to print, rather than only supporting existing files

### Changed
- Improved series page parsing to extract match types
- Changed script names

## [0.0.12]
### Added
- Parse Cricinfo season page to print all series in a season
- Generic models for Scorecards indepdent of Cricinfo, so they can be used elsewhere
- Better commenting

### Changed
- Renaming some attributes to what they actually represent rather than the Cricinfo terminology

## [0.0.11]
### Added
- Badges to readme

### Changed
- Simplified some models
- Renamed workspace and GitHub Action

## [0.0.10]
### Added
- Missing links, attributions & information in `pyproject` file
- Detail to `readme.md`

### Changed
- Renamed some folders and added imports to improve ease of use

### Fixed
- Some imports were in the optional section that should have been in main

## [0.0.9]
### Added
- Missing comments

## [0.0.8]
### Added
- Additional API router to return raw responses rather than parsing anything

## [0.0.7]
### Added
- Script to run the API

## [0.0.6]
### Changed
- Moved to `Hatchling` for building

## [0.0.5]
### Changed
- Renamed package to `pycricinfo`

## [0.0.4]
### Added
- Better config for handling Cricinfo API routes
- Models to represent more API entities

### Changed
- Move more logic into `Core` with Pydantic model parsing
- Move to UV package manager
- Format files with Ruff

## [0.0.3]
### Added
- Optional package component to create a wrapper for useful Cricinfo APIs

## [0.0.2]
### Added
- Output play-by-play commentary data

### Changed
- Generate requirements files using `pip-compile`

## [0.0.1]
### Added
- Output a scorecard from the JSON data of a match