'''Test aioretry_built_by_call_sync_param_int_any.py '''

# pylint: disable=unused-import, unused-argument, invalid-name, R0801


import asyncio
from typing import Any

from kaioretry import Retry, Context


aioretry_decorator = Retry(
    exceptions=(ValueError, NotImplementedError),
    context=Context(tries=5, delay=2)).aioretry

def func(x: int, y: int) -> Any:
    ''' ... '''
    return 'return_value'
func = aioretry_decorator(func)


async def use_decoration(parameter: str) -> str:
    ''' obtain result and use it '''
    result = await func(1, 2)
    assert isinstance(result, str)
    return f"parameter is {parameter}. result is {result}"


if __name__ == "__main__":
    print(asyncio.run(use_decoration("value")))
