"""Retry Context Implementation"""

import time
import random
import asyncio
import logging
import uuid

from typing import cast, Awaitable, Any, TypeVar
from collections.abc import Callable, Generator, AsyncGenerator

from .types import NonNegative, Number, Jitter


UpdateDelayF = Callable[[Number], Number]
SleepRetVal = TypeVar('SleepRetVal', None, Awaitable[None])
SleepF = Callable[[Number], SleepRetVal]


class _ContextIterator:
    """Single-usage helper class for Context objects."""

    # pylint: disable=too-few-public-methods

    def __init__(self, identifier: uuid.UUID, sleep: SleepF[Any], tries: int,
                 delay: NonNegative, update_delay: UpdateDelayF,
                 logger: logging.Logger, /) -> None:
        self.__identifier = identifier
        self.__sleep = sleep
        self.__delay = delay
        self.__update_delay = update_delay
        self.__logger = logger
        if tries > 0:
            self.__tries = tries
            self.__log_try = "%d tries remaining"
        else:
            self.__tries = -1
            self.__log_try = "try #%d"

    def __log(self, level: int, fmt: str, *args: Any) -> None:
        """Log a message with some more context"""
        self.__logger.log(level, f"{self.__identifier}: {fmt}", *args)

    def _sleep(self) -> SleepRetVal:
        self.__log(logging.INFO, "sleeping %s seconds", self.__delay)
        return cast(SleepRetVal, self.__sleep(self.__delay))

    def __iter__(self) -> Generator[SleepRetVal, None, None]:
        self.__tries -= 1
        while self.__tries:
            self.__log(logging.INFO, self.__log_try, abs(self.__tries))
            yield self._sleep()
            self.__delay = self.__update_delay(self.__delay)
            self.__tries -= 1


class Context:

    """The Retry Context will maintain the number of tries and the
    delay between those tries.

    It can act as both a :py:class:`~collections.abc.Generator` and an
    :py:class:`~collections.abc.AsyncGenerator`, and can be reused,
    multiple times, even with multiple
    :py:class:`~kaioretry.retry.Retry` instances.

    The :py:class:`~kaioretry.retry.Retry` objects will iterate over
    :py:class:`~kaioretry.context.Context`, synchronously, or
    asynchronously, depending of the nature of the decorated function.

    :param tries: the maximum number of iterations (a.k.a.: tries,
        function calls) to perform before exhaustion. A negative value
        means infinite. 0 is forbidden, since it would mean "don't
        run" at all.

    :param delay: the initial number of seconds to wait between two
        iterations. It must be non-negative. Default is 0 (no delay).

    :param backoff: a multiplier applied to the delay after each
        iteration. It can be a float, and it can actually be less than
        one. Default: 1 (no backoff).

    :param jitter: extra seconds added to delay between
        iterations. Default: 0.

    :param max_delay: the maximum value allowed for delay. If None
        (the default), then delay is unlimited. Cannot be negative.

    :param min_delay: the minimum value allowed for delay. Cannot be
        negative. Default is 0.

    :param logger: the :py:class:`logging.Logger` object to which the
        log messages will be sent to.

    :raises ValueError: if tries, min_delay or max_delay have incorrect values.
    :raises TypeError: if jitter is neither a Number or a tuple.

    """

    # pylint: disable=too-many-instance-attributes

    DEFAULT_LOGGER: logging.Logger = logging.getLogger(__name__)
    """The :py:class:`logging.Logger` object that will be used if none
    are provided to the constructor.
    """

    @classmethod
    def __make_jitter(cls, jitter: Jitter) -> UpdateDelayF:
        if isinstance(jitter, (int, float)):
            return cast(UpdateDelayF, jitter.__add__)
        if isinstance(jitter, (tuple, list)):
            return cast(UpdateDelayF,
                        lambda x: x + random.uniform(*jitter))
        raise TypeError("jitter parameter is neither a number "
                        f"nor a 2 length tuple: {jitter}")

    def __init__(self, *, tries: int = -1, delay: NonNegative = 0,
                 backoff: Number = 1, jitter: Jitter = 0,
                 max_delay: NonNegative | None = None,
                 min_delay: NonNegative = 0,
                 logger: logging.Logger = DEFAULT_LOGGER) -> None:
        if tries == 0:
            raise ValueError("tries value cannot be 0")
        self.__tries = tries
        self.__delay = delay
        self.__jitter = self.__make_jitter(jitter)
        self.__backoff = backoff
        if min_delay < 0:
            raise ValueError(
                f"min_delay cannot be less than 0. ({min_delay} given)")
        self.__min_delay = min_delay
        if max_delay is not None and max_delay < min_delay:
            raise ValueError(
                "min_delay cannot be greater than max_delay. "
                f"min given: {min_delay}. max given: {max_delay}")
        self.__max_delay = max_delay
        self.__str = (
            f"{self.__class__.__name__}("
            f"tries={tries}, "
            f"delay=({min_delay}<=({delay}+{jitter})*{backoff}<={max_delay}))")
        self.__logger = logger

    def __update_delay(self, delay: NonNegative) -> NonNegative:
        """Compute the updated values for given delay.

        :param delay: the current value of delay between iterations.

        :returns: the new duration to wait for before the next iteration.
        """
        delay = self.__jitter(delay * self.__backoff)
        if self.__max_delay is not None:
            delay = min(delay, self.__max_delay)
        delay = max(delay, self.__min_delay)
        return delay

    def __make_iterator(
            self, sleep: SleepF[Any]) -> Generator[SleepRetVal, None, None]:
        return iter(_ContextIterator(
            uuid.uuid4(), sleep, self.__tries, self.__delay,
            self.__update_delay, self.__logger))

    def __iter__(self) -> Generator[None, None, None]:
        yield
        yield from self.__make_iterator(time.sleep)

    async def __aiter__(self) -> AsyncGenerator[None, None]:
        yield
        for sleep in cast(Generator[Awaitable[None], None, None],
                          self.__make_iterator(asyncio.sleep)):
            await sleep
            yield

    def __str__(self) -> str:
        return self.__str


__all__ = ['Context']
