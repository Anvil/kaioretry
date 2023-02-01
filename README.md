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

I say *backward* because, while `retry` clearly did the job for me for a
time, at some point I've encountered a big limitation: it did not work
with asyncio coroutines. And it's been unmaintained for 6 years.

I found a few alternatives for that but none of them were both sync
and async and since I did not wanted to use 2 differents modules for
the same goal, I've decided to write this one, with the rule that the
code duplication, between the sync and async versions, should be
smartly kept to a very very strict minimum.

And here we are then.


# Documentation

API Documentation is available on readthedocs:
[https://kaioretry.readthedocs.io/en/latest/]


## TODO List

* Write a decent README
* Improve documentation display on the RTD
