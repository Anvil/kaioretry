# KaioRetry

[![PyPI version](https://img.shields.io/pypi/v/kaioretry?logo=pypi&style=plastic)](https://pypi.python.org/pypi/kaioretry/)
[![Supported Python Version](https://img.shields.io/pypi/pyversions/kaioretry?logo=python&style=plastic)](https://pypi.python.org/pypi/kaioretry/)
[![License](https://img.shields.io/pypi/l/kaioretry?color=green&logo=GNU&style=plastic)](https://github.com/Anvil/kaioretry/blob/main/LICENSE)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/kaioretry?color=magenta&style=plastic)](https://pypistats.org/packages/kaioretry)

[![Pylint Static Quality Github Action](https://github.com/Anvil/kaioretry/actions/workflows/pylint.yml/badge.svg)](https://github.com/Anvil/kaioretry/actions/workflows/pylint.yml)
[![Mypy Static Quality Github Action](https://github.com/Anvil/kaioretry/actions/workflows/mypy.yml/badge.svg)](https://github.com/Anvil/kaioretry/actions/workflows/mypy.yml)
[![Pylint Static Quality Github Action](https://github.com/Anvil/kaioretry/actions/workflows/python-app.yml/badge.svg)](https://github.com/Anvil/kaioretry/actions/workflows/python-app.yml)
[![Documentation Status](https://readthedocs.org/projects/kaioretry/badge/?version=latest)](https://kaioretry.readthedocs.io/en/latest/?badge=latest)


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


# Known Issues

## Pylint

[Pylint](https://pylint.readthedocs.io/en/latest/), it seems, is not [really
good a detecting decorators that change function
signatures](https://github.com/pylint-dev/pylint/issues/3108), and kaioretry
defines and uses a lot of decorators (relatively speaking).

This means that such basic code:

```python
from kaioretry import aioretry

@aioretry(exceptions=ZeroDivisionError)
async def func(x, y):
    return x / y
```

Will trigger the following pylint errors:

```
E1120: No value for argument 'retry_obj' in function call (no-value-for-parameter)
```

According to pylint documentation, the only way to widely work around this
issue is to use the
[`signature-mutators`](https://pylint.pycqa.org/en/latest/user_guide/configuration/all-options.html#signature-mutators)
feature of pylint. This can be done either on the command line:

```
pylint --signature-mutators=kaioretry._make_decorator
```

Or through pylint configuration file:

```ini
# The TYPECHECK section accepts a signature-mutators directive.
[TYPECHECK]

# List of decorators that change the signature of a decorated function.
signature-mutators=kaioretry._make_decorator
```

(Of course, you can inline a `# pylint: disable=no-value-for-parameter`
comment on all `aioretry()` and `retry()` call lines, and it can be good
enough to disable a one-time warning, but repeating that line can be
tedious. The `signature-mutators` directive will globally disable the
signature-checking for `aioretry()` and `retry()` calls, so this can be easier
depending of your own usage of kaioretry.)

# Feedback welcome.

Always.
