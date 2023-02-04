# Changelog

## [Unreleased]

## [0.7.0] - 2023-02-04

### Changed
- update the `Retry.__call__` heuristic to include regular functions returning
  awaitable objects.


## [0.6.0] - 2023-02-01

### Changed
- Lower python requirement to 3.10

### Added
- flake8, pylint and unit tests python 3.10 and 3.11

## [0.5.0] - 2023-01-31

### Changed
- Refactored sync/async Context loops implementations.

## [0.4.0] - 2023-01-29

### Added
- tools/merge and tools/set-version scripts

### Changed
- Update overall docstrings
- Opt out of typing module when deprecated
- Refactor kaioretry.retry and kaioretry.aioretry through another
  decorator.
- Expose logger parameter in kaioretry.retry and kaioretry.aioretry
  signatures.
- Fix return description in kaioretry.retry and kaioretry.aioretry
  docstrings.

## [0.3.0] - 2023-01-29

### Fixed
- Make the decoration have the decorated docstring and signature for
  introspection.

## [0.2.0] - 2023-01-26

### Added

- Basic logging features to Context and Retry classes
- Add this changelog

## [0.1.3] - 2023-01-25

### Added

- Publication on pypi with adequate classifers and stuff

## [0.1.0] - 2023-01-24

### Added

- First release
