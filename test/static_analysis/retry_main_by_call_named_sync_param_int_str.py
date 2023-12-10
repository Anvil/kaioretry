'''Test retry_main_by_call_named_sync_param_int_str.py '''

# pylint: disable=unused-import, unused-argument, invalid-name, R0801


import asyncio
from typing import Any
from collections.abc import Callable, Awaitable
from mypy_extensions import VarArg, KwArg
from kaioretry import retry, aioretry, Retry, Context


def func(x: int, y: int) -> str:
    ''' ... '''
    return 'return_value'

wrapped: Callable[[int, int], str] = retry(exceptions=Exception, tries=2)(func)


async def use_decoration(parameter: str) -> str:
    ''' obtain result and use it '''
    result = wrapped(1, 2)
    assert isinstance(result, str)
    return f"parameter is {parameter}. result is {result}"


if __name__ == "__main__":
    print(asyncio.run(use_decoration("value")))
