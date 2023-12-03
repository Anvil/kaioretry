'''Test aioretry_main_by_call_unnamed_async_kwargs_int_any.py '''

# pylint: disable=unused-import, unused-argument, invalid-name, R0801


import asyncio
from typing import Any

from kaioretry import aioretry


aioretry_decorator = aioretry(Exception, 2)


async def func(**kwargs: int) -> Any:
    ''' ... '''
    return 'return_value'
func = aioretry_decorator(func)


async def use_decoration(parameter: str) -> str:
    ''' obtain result and use it '''
    result = await func(x=1, y=2)
    return f"parameter is {parameter}. result is {result}"


if __name__ == "__main__":
    asyncio.run(use_decoration("value"))