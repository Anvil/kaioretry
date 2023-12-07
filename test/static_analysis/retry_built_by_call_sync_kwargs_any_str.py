'''Test retry_built_by_call_sync_kwargs_any_str.py '''

# pylint: disable=unused-import, unused-argument, invalid-name, R0801


import asyncio
from typing import Any

from kaioretry import Retry, Context


aioretry_decorator = Retry(
    exceptions=(ValueError, NotImplementedError),
    context=Context(tries=5, delay=2)).retry

def func(**kwargs: Any) -> str:
    ''' ... '''
    return 'return_value'
func = aioretry_decorator(func)


async def use_decoration(parameter: str) -> str:
    ''' obtain result and use it '''
    result = func(x=1, y=2)
    assert isinstance(result, str)
    return f"parameter is {parameter}. result is {result}"


if __name__ == "__main__":
    print(asyncio.run(use_decoration("value")))
