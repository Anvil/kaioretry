"""kaioretry.context.Context class unit tests"""

import random
import logging
import pytest
import pytest_cases
from kaioretry.context import Context


async def assert_context_length(context, length):
    """*Synchronously* unroll the a Context object and assert its length"""
    assert len(list(context)) == length


async def assert_context_async_length(context, length):
    """*Asynchronously* unroll the a Context object and assert its length"""
    assert len([x async for x in context]) == length


@pytest_cases.fixture(
    unpack_into="assert_length, sleep",
    params=("sync", "async"))
def sync_async(request, ssleep, asleep):
    """Yield the matching assert_context_legnth and sleep functions"""
    if request.param == "async":
        yield assert_context_async_length, asleep
    else:
        yield assert_context_length, ssleep


@pytest.mark.parametrize(
    "params", ({"tries": 0},
               {"jitter": "asdf"},
               {"min_delay": random.randint(-1000, -1)},
               {"min_delay": random.randint(50, 100),
                "max_delay": random.randint(1, 50)}))
def test_context_bad_param(params):
    """Test that bad params values/types trigger matching exceptions"""
    with pytest.raises((ValueError, TypeError)):
        Context(**params)


@pytest.mark.parametrize("tries", (1, random.randint(2, 37)))
async def test_context_tries(assert_length, sleep, tries):
    """Test the length of iter(context), and the number of delaying
    operation. If tries == 1, no delay should have been performed.
    """
    context = Context(tries=tries)
    await assert_length(context, tries)
    assert sleep.call_count == tries - 1


async def test_context_logging(mocker, assert_length, sleep):
    """Test that the passed logger is actually used"""
    tries = random.randint(2, 10)
    logger = mocker.MagicMock(spec=logging.Logger)
    context = Context(tries=tries, logger=logger)
    await assert_length(context, tries)
    sleep.assert_called()
    assert logger.method_calls


@pytest.mark.parametrize(
    "update_delay", (lambda x: x, lambda _: random.randint(3, 10)))
async def test_context_delay_first_unaltered(
        assert_length, sleep, update_delay):
    """Test that jitter and backoff do not alter the first value of delay"""
    tries = 2
    delay = random.randint(1, 100)
    context = Context(tries=tries, delay=delay, update_delay=update_delay)
    await assert_length(context, tries)
    sleep.assert_called_once_with(delay)


@pytest.mark.parametrize(
    "delay, max_delay, expected, update_delay",
    ((5, 6, 5, lambda x: x),
     (5, 6, 6, lambda x: x + random.randint(3, 10))))
async def test_context_max_delay(
        mocker, assert_length, sleep, delay, max_delay, expected, update_delay):
    # pylint: disable=too-many-arguments
    """context delay should not grow bigger than max_delay"""
    tries = 3
    update_delay_mock = mocker.MagicMock(side_effect=update_delay)
    context = Context(tries=tries, delay=delay, max_delay=max_delay,
                      update_delay=update_delay_mock)
    await assert_length(context, tries)

    sleep.assert_any_call(delay)
    sleep.assert_any_call(expected)
    update_delay_mock.assert_any_call(delay)
