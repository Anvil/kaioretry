"""Retry class unit tests"""

from random import randint, choice
from inspect import getfullargspec
import pytest

from kaioretry import Retry, Context
from .mock import MagicMock
from .conftest import for_each_is_func_async_case


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


async def test_retry_final_failure(exceptions, decorator, func, assert_result):
    """When tries are exhausted, the last raised exception should be
    propagated by the decorator"""
    side_effect = [choice(exceptions)() for _ in range(randint(1, 10))]

    func.side_effect = side_effect

    retry = Retry(exceptions, context=Context(tries=len(side_effect)))
    retryable = decorator(retry, func)

    assert retryable is not func
    with pytest.raises(exceptions) as exc_info:
        await assert_result(retryable(), None)

    # The last raised exception is the last in the side_effect List.
    assert exc_info.value is side_effect[-1]


@pytest.mark.parametrize("is_async", (True, False))
async def test_retry___call__(exception, mocker, is_async):
    """Test that __call__ return a same-nature decorated function"""
    mocker.patch("kaioretry.Retry.is_func_async", return_value=is_async)
    mocker.patch("kaioretry.Retry.retry", return_value=not is_async)
    mocker.patch("kaioretry.Retry.aioretry", return_value=is_async)

    retry = Retry(exception)
    retryable = retry(MagicMock())

    assert retryable


@for_each_is_func_async_case
async def test_retry_is_func_async(function, is_async):
    """Test that Retry.is_func_async result matches expectations"""
    assert Retry.is_func_async(function) == is_async
