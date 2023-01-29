"""Common unit tests fixtures"""

import inspect
import string
from random import choice

import pytest
import pytest_cases

from kaioretry import Retry

# This is a copy of Lib/unit/mock.py from github, since my local
# python 3.11.1 does not have iso-functionning MagicMock and
# AsyncMock. This copy includes the fix for
# create_autospec(async_def), which is addressed by:
# https://github.com/python/cpython/pull/94962
from .mock import create_autospec


def _sync(first=1, second=2, third=3):
    """A stupid sync function"""
    # pylint: disable=unused-argument
    return 10


async def _async(first=1, second=2, third=3):
    """A stupid async function"""
    # pylint: disable=unused-argument
    return 10


def random_string(length=10):
    """Return a random string"""
    return ''.join(choice(string.ascii_lowercase) for _ in range(length))


def auto_spec(func):
    """Return an autospec-ed mock from a given function"""
    mock = create_autospec(func)
    mock.__qualname__ = mock.__name__ = random_string()
    mock.__doc__ = random_string()
    return mock


@pytest.fixture(params=(_sync, _async))
def any_func(request):
    """Provide a mock impersonating a function or async function"""
    return auto_spec(request.param)


@pytest.fixture
def ssleep(mocker):
    """Mock time.sleep"""
    return mocker.patch("time.sleep")


@pytest.fixture
def asleep(mocker):
    """Mock asyncio.sleep, and check that it's been correctly awaited
    in the end.
    """
    mock = mocker.patch("asyncio.sleep")
    yield mock
    assert mock.await_count == mock.call_count


async def assert_async_result(result, expected):
    """Check that a given object, once awaited, returns a given
    expected result.
    """
    assert inspect.isawaitable(result)
    assert await result == expected


async def assert_sync_result(result, expected):
    """Check that a given object has an expected value. Note that
    function is a coroutine function, to match assert_async_result.
    """
    assert result == expected


@pytest_cases.fixture(
    unpack_into="decorator, func, assert_result",
    params=((Retry.retry, _sync, assert_sync_result),
            (Retry.aioretry, _sync, assert_async_result),
            (Retry.aioretry, _async, assert_async_result)),
    ids=("sync-sync", "async-sync", "async-async"))
def supported_cases(request):
    """Provides the working combos decorator / func / validation of result"""
    decorator, func, assert_result = request.param
    mock = create_autospec(func)
    yield decorator, mock, assert_result
    if inspect.iscoroutinefunction(func):
        assert mock.await_count == mock.call_count


@pytest.fixture
def exception():
    """Generate a new uniq exception class"""
    class _AnotherError(Exception):
        pass
    return _AnotherError
