"""kaioretry.context.Context class unit tests"""

import random
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


@pytest.mark.parametrize("jitter", (0, random.randint(2, 10)))
@pytest.mark.parametrize("backoff", (1, random.randint(3, 10)))
async def test_context_delay_first_unaltered(assert_length, sleep, jitter, backoff):
    """Test that jitter and backoff do not alter the first value of delay"""
    tries = 2
    delay = random.randint(1, 100)
    context = Context(tries=tries, delay=delay, jitter=jitter, backoff=backoff)
    await assert_length(context, tries)
    sleep.assert_called_once_with(delay)


@pytest.mark.parametrize("jitter", (0, random.randint(2, 10)))
@pytest.mark.parametrize("backoff", (1, random.randint(3, 10)))
async def test_context_max_delay(assert_length, sleep, jitter, backoff):
    """context delay should not grow bigger than max_delay"""
    tries = 3
    delay = 5
    max_delay = delay + 1
    if jitter == 0 and backoff == 1:
        second_call = delay
    else:
        second_call = max_delay
    context = Context(tries=tries, delay=delay, max_delay=max_delay,
                      jitter=jitter, backoff=backoff)
    await assert_length(context, tries)
    sleep.assert_any_call(delay)
    sleep.assert_any_call(second_call)


async def test_context_random_jitter(assert_length, sleep):
    """Test random interval for jitter as Context parameter"""
    min_jitter = random.randint(1, 10)
    max_jitter = min_jitter + random.randint(1, 10)
    delay = 1
    tries = 3

    context = Context(
        tries=tries, delay=delay, jitter=(min_jitter, max_jitter))
    await assert_length(context, tries)

    # Second and last call should have been made with delay + jitter.
    assert delay + min_jitter < sleep.call_args[0][0] < delay + max_jitter
