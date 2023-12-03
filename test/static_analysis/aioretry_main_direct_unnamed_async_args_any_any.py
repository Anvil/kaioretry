'''Test aioretry_main_direct_unnamed_async_args_any_any.py '''

# pylint: disable=unused-import, unused-argument, invalid-name, R0801


import asyncio
from typing import Any

from kaioretry import aioretry


@aioretry(Exception, 2)
async def func(*args: Any) -> Any:
    ''' ... '''
    return 'return_value'


async def use_decoration(parameter: str) -> str:
    ''' obtain result and use it '''
    result = await func(1, 2)
    return f"parameter is {parameter}. result is {result}"


if __name__ == "__main__":
    asyncio.run(use_decoration("value"))
