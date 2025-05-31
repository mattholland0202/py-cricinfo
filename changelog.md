# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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