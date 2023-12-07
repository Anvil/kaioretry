'''Test retry_main_by_call_unnamed_sync_args_any_any.py '''

# pylint: disable=unused-import, unused-argument, invalid-name, R0801


import asyncio
from typing import Any

from kaioretry import retry


aioretry_decorator = retry(Exception, 2)


def func(*args: Any) -> Any:
    ''' ... '''
    return 'return_value'
func = aioretry_decorator(func)


async def use_decoration(parameter: str) -> str:
    ''' obtain result and use it '''
    result = func(1, 2)
    assert isinstance(result, str)
    return f"parameter is {parameter}. result is {result}"


if __name__ == "__main__":
    print(asyncio.run(use_decoration("value")))
