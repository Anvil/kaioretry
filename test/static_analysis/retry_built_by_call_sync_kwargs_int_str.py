'''Test retry_built_by_call_sync_kwargs_int_str.py '''

# pylint: disable=unused-import, unused-argument, invalid-name, R0801


import asyncio
from typing import Any
from collections.abc import Callable, Awaitable
from mypy_extensions import VarArg, KwArg
from kaioretry import retry, aioretry, Retry, Context


def func(**kwargs: int) -> str:
    ''' ... '''
    return 'return_value'

wrapped: Callable[[KwArg(int)], str] = Retry(exceptions=(ValueError, NotImplementedError), context=Context(tries=5, delay=2)).retry(func)


async def use_decoration(parameter: str) -> str:
    ''' obtain result and use it '''
    result = wrapped(x=1, y=2)
    assert isinstance(result, str)
    return f"parameter is {parameter}. result is {result}"


if __name__ == "__main__":
    print(asyncio.run(use_decoration("value")))