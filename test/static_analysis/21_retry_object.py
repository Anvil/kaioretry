"""Retry object, with __call__, no param"""

from kaioretry import Retry

@Retry()
def func(param1: int) -> float:
    """ one of """
    return 1 / param1


def func2(param2: int) -> float:
    """Anything using the first func"""
    return 3 + func(param2)


if __name__ == "__main__":
    assert func(1) == 1
