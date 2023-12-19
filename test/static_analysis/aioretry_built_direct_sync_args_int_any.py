'''Test aioretry_built_direct_sync_args_int_any.py '''

# flake8: noqa
# pylint: disable=unused-import, unused-argument, invalid-name, R0801


import asyncio
from typing import Any
from collections.abc import Callable, Awaitable
from mypy_extensions import VarArg, KwArg
from kaioretry import retry, aioretry, Retry, Context


@Retry(exceptions=(ValueError, NotImplementedError), context=Context(tries=5, delay=2)).aioretry
def func(*args: int) -> Any:
    ''' ... '''
    return 'return_value'


async def use_decoration(parameter: str) -> str:
    ''' obtain result and use it '''
    result = await func(1, 2)
    assert isinstance(result, str)
    return f"parameter is {parameter}. result is {result}"


if __name__ == "__main__":
    print(asyncio.run(use_decoration("value")))
