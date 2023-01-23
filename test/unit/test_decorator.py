"""Retry class unit tests"""

import random
from inspect import isawaitable, iscoroutinefunction
from unittest.mock import MagicMock, AsyncMock
import pytest

from kaioretry import Retry, Context


def test_retry(exception):
    """Test for retry until success"""
    result = random.randint(1, 10000000)
    side_effect = [exception] * random.randint(1, 10) + [result]

    mock = MagicMock(side_effect=side_effect)

    retry = Retry(exception)
    retryable = retry.retry(mock)

    assert retryable is not mock
    assert retryable() == result
    assert mock.call_count == len(side_effect)


@pytest.mark.parametrize("mock", (MagicMock(), AsyncMock()))
async def test_aioretry(exception, mock):
    """Test that Retry.aioretry works with both functions and
    coroutine functions.
    """
    result = random.randint(1, 10000000)
    side_effect = [exception] * random.randint(1, 10) + [result]

    mock.side_effect = side_effect

    retry = Retry(exception)
    retryable = retry.aioretry(mock)
    coro = retryable()

    assert retryable is not mock
    assert isawaitable(coro)
    assert await coro == result
    assert mock.call_count == len(side_effect)


async def test_retry_final_failure(exception, mock, assert_result):
    """When tries are exhausted, the last raised exception should be
    propagated by the decorator"""
    side_effect = [exception() for _ in range(random.randint(1, 10))]

    mock.side_effect = side_effect

    retry = Retry(exception, context=Context(tries=len(side_effect)))
    retryable = retry(mock)

    assert retryable is not mock
    with pytest.raises(exception) as exc_info:
        await assert_result(retryable(), None)

    # The last raised exception is the last in the side_effect List.
    assert exc_info.value is side_effect[-1]


@pytest.mark.parametrize("mock_cls", (MagicMock, AsyncMock))
async def test_retry___call__(exception, mock_cls):
    """Test that __call__ return a same-nature decorated function"""
    mock = mock_cls()
    retry = Retry(exception)

    retryable = retry(mock)

    assert iscoroutinefunction(retryable) == iscoroutinefunction(mock)
