"""Common unit tests fixtures"""

import inspect
from unittest.mock import MagicMock

import pytest
import pytest_cases


# This is a copy of Lib/unit/mock.py from github, since my local
# python 3.11.1 does not have iso-functionning MagicMock and
# AsyncMock. This copy includes the fix for
# create_autospec(async_def), which is addressed by:
# https://github.com/python/cpython/pull/94962
from .mock import AsyncMock, create_autospec


def __f(x=1, y=2, z=3):
    return 10


async def __g(x=1, y=2, z=3):
    return 10


@pytest.fixture(params=(__f, __g))
def any_mock(request):
    """Provide a {Magic,Async}mock"""
    mock = create_autospec(request.param)
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


@pytest_cases.fixture(unpack_into="mock, assert_result")
def just_a_mock(any_mock):
    # pylint: disable=redefined-outer-name
    """Give a sync or async mock, with a matching coroutine function
    able to check its result.
    """
    if isinstance(any_mock, AsyncMock):
        yield any_mock, assert_async_result
        assert any_mock.await_count == any_mock.call_count
    else:
        yield any_mock, assert_sync_result


@pytest.fixture
def exception():
    """Generate a new uniq exception class"""
    class _AnotherError(Exception):
        pass
    return _AnotherError
