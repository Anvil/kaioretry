# KaioRetry

[![PyPI version](https://img.shields.io/pypi/v/kaioretry?logo=pypi&style=plastic)](https://pypi.python.org/pypi/kaioretry/)
[![Supported Python Version](https://img.shields.io/pypi/pyversions/kaioretry?logo=python&style=plastic)](https://pypi.python.org/pypi/kaioretry/)
[![License](https://img.shields.io/pypi/l/kaioretry?color=green&logo=GNU&style=plastic)](https://github.com/Anvil/kaioretry/blob/main/LICENSE)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/kaioretry?color=magenta&style=plastic)](https://pypistats.org/packages/kaioretry)

[![Pylint Static Quality Github Action](https://github.com/Anvil/kaioretry/actions/workflows/pylint.yml/badge.svg)](https://github.com/Anvil/kaioretry/actions/workflows/pylint.yml)
[![Pylint Static Quality Github Action](https://github.com/Anvil/kaioretry/actions/workflows/python-app.yml/badge.svg)](https://github.com/Anvil/kaioretry/actions/workflows/python-app.yml)


KaioRetry is (yet another) retry decorator implementation, which is
clearly inspired by the original
[retry](https://pypi.org/project/retry) module and is actually
backward compatible with it.

# Basic usage

Transparently perform retries on failures:

```python

from kaioretry import retry, aioretry


@retry(exceptions=ValueError, tries=2)
def some_func(...):
    ...


@aioretry(exceptions=(ValueError, SomeOtherError), tries=-1, delay=1)
async def some_coroutine(...):
    ...

```

# Documentation

If you care to read more, a more lengthy documentation is available on
[readthedocs](https://kaioretry.readthedocs.io/en/latest/).


### Feedback welcome.
