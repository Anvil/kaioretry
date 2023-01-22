"""Common unit tests fixtures"""

import inspect
import pytest
import pytest_cases


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
    unpack_into="mock, assert_result",
    params=("sync", "async"))
def just_a_mock(request, mocker):
    """Give a sync or async mock, with a matching coroutine function
    able to check its result.
    """
    if request.param == "sync":
        yield mocker.MagicMock(), assert_sync_result
    else:
        mock = mocker.AsyncMock()
        yield mock, assert_async_result
        assert mock.await_count == mock.call_count


@pytest.fixture
def exception():
    """Generate a new uniq exception class"""
    class _AnotherError(Exception):
        pass
    return _AnotherError
