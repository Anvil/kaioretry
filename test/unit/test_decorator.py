"""Retry class unit tests"""

import string
from random import randint, choice
from inspect import isawaitable, iscoroutinefunction
import pytest

from kaioretry import Retry, Context

def random_string(length=10):
    """Return a random string"""
    letters = string.ascii_lowercase
    return ''.join(choice(letters) for _ in range(length))


def configure_callable_mock(mock):
    """Configure a mock to act as a regularly-defined function"""
    mock.__name__ = random_string()


def test_retry(mocker, exception):
    """Test for retry until success"""
    result = randint(1, 10000000)
    side_effect = [exception] * randint(1, 10) + [result]
    logger = mocker.MagicMock()

    mock = mocker.MagicMock(side_effect=side_effect)
    configure_callable_mock(mock)

    retry = Retry(exception, logger=logger)
    retryable = retry.retry(mock)

    assert retryable is not mock
    assert retryable() == result
    assert mock.call_count == len(side_effect)
    assert logger.method_calls


async def test_aioretry(mocker, exception, any_mock):
    """Test that Retry.aioretry works with both functions and
    coroutine functions.
    """
    result = randint(1, 10000000)
    side_effect = [exception] * randint(1, 10) + [result]
    logger = mocker.MagicMock()

    any_mock.side_effect = side_effect
    configure_callable_mock(any_mock)

    retry = Retry(exception, logger=logger)
    retryable = retry.aioretry(any_mock)
    coro = retryable()

    assert retryable is not any_mock
    assert isawaitable(coro)
    assert await coro == result
    assert any_mock.call_count == len(side_effect)
    assert logger.method_calls


async def test_retry_final_failure(exception, mock, assert_result):
    """When tries are exhausted, the last raised exception should be
    propagated by the decorator"""
    side_effect = [exception() for _ in range(randint(1, 10))]

    mock.side_effect = side_effect
    configure_callable_mock(mock)

    retry = Retry(exception, context=Context(tries=len(side_effect)))
    retryable = retry(mock)

    assert retryable is not mock
    with pytest.raises(exception) as exc_info:
        await assert_result(retryable(), None)

    # The last raised exception is the last in the side_effect List.
    assert exc_info.value is side_effect[-1]


async def test_retry___call__(exception, any_mock):
    """Test that __call__ return a same-nature decorated function"""
    retry = Retry(exception)
    retryable = retry(any_mock)

    assert iscoroutinefunction(retryable) == iscoroutinefunction(any_mock)
