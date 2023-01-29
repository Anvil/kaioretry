"""Retry class unit tests"""

from random import randint
from inspect import iscoroutinefunction, getfullargspec
import pytest

from kaioretry import Retry, Context
from .mock import MagicMock


async def test_retry(exception, decorator, func, assert_result):
    """Test the decorator methods of the Retry class"""
    result = randint(1, 10000000)
    side_effect = [exception] * randint(1, 10) + [result]
    logger = MagicMock()

    func.side_effect = side_effect

    retry = Retry(exception, logger=logger)
    retryable = decorator(retry, func)

    assert retryable is not func
    assert retryable.__doc__ == func.__doc__
    assert getfullargspec(retryable) == getfullargspec(func)

    await assert_result(retryable(), result)
    assert func.call_count == len(side_effect)
    assert logger.method_calls


async def test_retry_final_failure(exception, decorator, func, assert_result):
    """When tries are exhausted, the last raised exception should be
    propagated by the decorator"""
    side_effect = [exception() for _ in range(randint(1, 10))]

    func.side_effect = side_effect

    retry = Retry(exception, context=Context(tries=len(side_effect)))
    retryable = decorator(retry, func)

    assert retryable is not func
    with pytest.raises(exception) as exc_info:
        await assert_result(retryable(), None)

    # The last raised exception is the last in the side_effect List.
    assert exc_info.value is side_effect[-1]


async def test_retry___call__(exception, any_func):
    """Test that __call__ return a same-nature decorated function"""
    retry = Retry(exception)
    retryable = retry(any_func)

    assert iscoroutinefunction(retryable) == iscoroutinefunction(any_func)
