"""Common unit tests fixtures"""

import asyncio
import inspect
import string
from random import choice
from typing import Awaitable
import collections.abc


import pytest
import pytest_cases

from kaioretry import Retry

# This is a copy of Lib/unit/mock.py from github, since my local
# python 3.11.1 does not have iso-functionning MagicMock and
# AsyncMock. This copy includes the fix for
# create_autospec(async_def), which is addressed by:
# https://github.com/python/cpython/pull/94962
from .mock import create_autospec


def _sync(first=1, second=2):
    """A stupid sync function"""
    # pylint: disable=unused-argument
    return 10


async def _async(first=1, second=2):
    """A stupid async function"""
    # pylint: disable=unused-argument
    return 10


def async_disguises():
    """Return the combinations of annotated functions that should be suitable
    for an async decoration.
    """
    for awaitable in (Awaitable, collections.abc.Awaitable):
        for rtype in (awaitable, awaitable[None]):
            # This cell-var case is not true for annotations, it seems.
            # pylint: disable=cell-var-from-loop
            def _async_in_disguise(first=1, second=2) -> rtype:
                # pylint: disable=unused-argument
                return asyncio.sleep(0)
            yield _async_in_disguise


def random_string(length=10):
    """Return a random string"""
    return ''.join(choice(string.ascii_lowercase) for _ in range(length))


def auto_spec(func):
    """Return an autospec-ed mock from a given function"""
    mock = create_autospec(func)
    mock.__qualname__ = mock.__name__ = random_string()
    mock.__doc__ = random_string()
    return mock


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


_is_func_async_cases_list = ((_sync, False),
                             (_async, True),
                             *[(async_in_disguise, True)
                               for async_in_disguise in async_disguises()])


_is_func_async_cases_ids = (
    "sync", "async", "sync-typing.awaitable", "sync-awaitable-typed",
    "sync-abc.awaitable", "sync-abc.awaitable-typed")


for_each_is_func_async_case = \
    pytest.mark.parametrize(
        "function, is_async", _is_func_async_cases_list,
        ids=_is_func_async_cases_ids)


@pytest_cases.fixture(unpack_into="decorator, func, assert_result",
                      params=((_sync, True), *_is_func_async_cases_list),
                      ids=("sync-as-async", *_is_func_async_cases_ids))
def retry_supported_cases(request):
    """Provides the working combos decorator / func / validation of result"""
    func, is_async = request.param
    if is_async:
        decorator, assert_result = Retry.aioretry, assert_async_result
    else:
        decorator, assert_result = Retry.retry, assert_sync_result
    mock = create_autospec(func)
    yield decorator, mock, assert_result
    if inspect.iscoroutinefunction(func):
        assert mock.await_count == mock.call_count


def _exception():
    class _AnotherError(Exception):
        pass
    return _AnotherError


@pytest.fixture
def exception():
    """Generate a new uniq exception class"""
    return _exception()


@pytest.fixture(params=(1, 2))
def exceptions(request):
    return tuple(_exception() for _ in range(request.param))
