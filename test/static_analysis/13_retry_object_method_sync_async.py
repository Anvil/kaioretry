"""Retry object, with __call__, no param"""

import asyncio
from kaioretry import Retry

@Retry().aioretry
def func(param1: int) -> float:
    """ one of """
    return 1 / param1


async def func2(param2: int) -> float:
    """Anything using the first func"""
    return 3 + await func3(await func(param2))


async def func3(param3: float) -> float:
    return param3 + 3


if __name__ == "__main__":
    assert asyncio.run(func(1)) == 1
