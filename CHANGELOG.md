# Changelog



## Unreleased
---

### New
* drop python 3.10 support

### Changes

### Fixes

### Breaks


## 1.1.2 - (2025-02-21)
---

### Fixes
* fix previous commit...


## 1.1.1 - (2025-02-21)
---

### Fixes
* add missing sphinx.configuration directive in readthedocs configuration file


## 1.1.0 - (2025-02-21)
---

### New
* add python 3.13 pipelines

### Changes
* blacken source code
* Convert pyproject to a more standard format
* Update to poetry 2.1

### Fixes
* fix decorators docstrings
* fix pipelines


## 1.0.2 - (2023-12-19)
---

### Fixes
* minor improvement to log messages
* improve flake8 of source and tests


## 1.0.1 - (2023-12-17)
---

### Changes
* update AioretryProtocol documentation

### Fixes
* minor documentation improvements


## 1.0.0 - (2023-12-16)
---

### Changes
* Annotate class attributes as Final

### Fixes
* fix kaioretry.{retry,aioretry} metadata and related sphinx documentation


## 0.12.3 - (2023-12-13)
---

### Fixes
* fix the reveal_type statement bloc in generated static-analysis test files
  and also reveal both function and decoration when possible


## 0.12.2 - (2023-12-13)
---

### Fixes
* finally fixed kaioretry._make_decorator type hinting issue
* remove trailing spaces in generated static-analysis files in the reveal_type
  code block


## 0.12.1 - (2023-12-10)
---

### Changes
* use generated static analysis test files instead of the few manually written
  ones. 184/217 of them are currently passing.
* rely on functools.wraps to avoid too much internal code


## 0.12.0 - (2023-12-03)
---

### New
* describe pylint issue in README.md

### Changes
* remove the need for decorator dependency


## 0.11.2 - (2023-12-02)
---

### Fixes
* fix retry/aioretry decorators type hints


## 0.11.1 - (2023-11-25)
---

### Fixes
* Add missing sphinx-rtd-theme documentation dependencies


## 0.11.0 - (2023-11-25)
---

### New
- Add python 3.12 support

### Changes
- Use changelog-cli to handle changelog and version

### Fixes
- minor issue in aioretry docstring format
- Fix Context and _ContextIterator type thing


## [0.10.2] - 2023-05-29

### Changes
- Some minor documentation updates

## [0.10.1] - 2023-05-29

### New
- Introduce AioretryCoro, AwaitableFunc and AnyFunction type aliases

## [0.10.0] - 2023-05-28

### New
- Add mypy github action and its badge

### Changes
- Update all decorators type annotations in order to allow kaioretry end-users
  to type-lint their code

## [0.9.4] - 2023-05-28

### Fixes
- Fix previous fix -_-

## [0.9.3] - 2023-05-28

### Fixes
- Fix ExceptionT and UpdateDelayF naming issues

## [0.9.2] - 2023-05-19

### Fixes
- Make type checkers know we have type informations

## [0.9.1] - 2023-02-25

### Changes
- update kaioretry.decorator module documentation
- update kaioretry.context module documentation

## [0.9.0] - 2023-02-25

### Changes
- make set-version abort if changelog has not been filled.
- use a function instead of jitter/backoff parameter in kaioretry.Context
  constructor

## [0.8.4] - 2023-02-09

### Fixes
- fix some typoes, spelling, grammar, etc in getting-started.rst.

## [0.8.3] - 2023-02-08

### Changes
- improve README.md a bit.

## [0.8.2] - 2023-02-08

### Fixes
- fix version in conf.py

## [0.8.1] - 2023-02-08

### Changes
- make set-version exit on error

### Fixes
- poetry-core version in pyproject.toml

## [0.8.0] - 2023-02-08

### New
- add plenty of sphinx documentation

## [0.7.1] - 2023-02-04

### Fixes
- fix a minor pylintness issue

## [0.7.0] - 2023-02-04

### Changes
- update the `Retry.__call__` heuristic to include regular functions returning
  awaitable objects.

## [0.6.0] - 2023-02-01

### Changes
- Lower python requirement to 3.10

### New
- flake8, pylint and unit tests python 3.10 and 3.11

## [0.5.0] - 2023-01-31

### Changes
- Refactored sync/async Context loops implementations.

## [0.4.0] - 2023-01-29

### New
- tools/merge and tools/set-version scripts

### Changes
- Update overall docstrings
- Opt out of typing module when deprecated
- Refactor kaioretry.retry and kaioretry.aioretry through another
  decorator.
- Expose logger parameter in kaioretry.retry and kaioretry.aioretry
  signatures.
- Fix return description in kaioretry.retry and kaioretry.aioretry
  docstrings.

## [0.3.0] - 2023-01-29

### Fixes
- Make the decoration have the decorated docstring and signature for
  introspection.

## [0.2.0] - 2023-01-26

### New

- Basic logging features to Context and Retry classes
- Add this changelog

## [0.1.3] - 2023-01-25

### New

- Publication on pypi with adequate classifers and stuff

## [0.1.0] - 2023-01-24

### New

- First release
