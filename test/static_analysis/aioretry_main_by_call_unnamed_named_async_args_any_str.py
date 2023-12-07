'''Test aioretry_main_by_call_unnamed_named_async_args_any_str.py '''

# pylint: disable=unused-import, unused-argument, invalid-name, R0801


import asyncio
from typing import Any

from kaioretry import aioretry


aioretry_decorator = aioretry(exceptions=Exception, tries=2)


async def func(*args: Any) -> str:
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
