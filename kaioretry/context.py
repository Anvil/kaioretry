"""Retry Context Implementation"""

import time
import random
import asyncio
import logging

from typing import AsyncGenerator, Generator, cast, Callable

from .types import NonNegative, Number, Jitter


JitterFunc = Callable[[Number], Number]


class Context:

    """The Retry Context will maintain the number of tries and the
    delay between those tries.

    It can act as both a Generator and an AsyncGenerator, and can be
    reused, multiple times, even with multiple Retry instances.

    The Retry objects will iterate over Context, synchronously, or
    asynchronously, depending of the nature of the decorated function.

    :param tries: the maxi number of iterations (a.k.a.: tries,
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
        negative.

    :raises ValueError: if tries, min_delay or max_delay have incorrect values.
    :raises TypeError: if jitter is neither a Number or a tuple.
    """

    # pylint: disable=too-many-instance-attributes

    DEFAULT_LOGGER = logging.getLogger(__name__)

    @classmethod
    def __make_jitter(cls, jitter: Jitter) -> JitterFunc:
        if isinstance(jitter, (int, float)):
            return cast(JitterFunc, jitter.__add__)
        if isinstance(jitter, (tuple, list)):
            return cast(JitterFunc,
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

    def update(self, delay: NonNegative) -> NonNegative:
        """Return the updated values for tries and delay.

        :param delay: the current value of delay between iterations.

        :returns: the number of tries left _and_ the duration to wait
            for before the next iteration.

        """
        delay = self.__jitter(delay * self.__backoff)
        if self.__max_delay is not None:
            delay = min(delay, self.__max_delay)
        delay = max(delay, self.__min_delay)
        return delay

    def __iter__(self) -> Generator[None, None, None]:
        yield
        tries, delay = self.__tries, self.__delay
        while tries := tries - 1:
            self.__logger.info("sleeping %s seconds", delay)
            time.sleep(delay)
            yield
            delay = self.update(delay)

    async def __aiter__(self) -> AsyncGenerator[None, None]:
        yield
        tries, delay = self.__tries, self.__delay
        while tries := tries - 1:
            self.__logger.info("sleeping %s seconds", delay)
            await asyncio.sleep(delay)
            yield
            delay = self.update(delay)

    def __str__(self) -> str:
        return self.__str


__all__ = ['Context']
