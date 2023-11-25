"""A Retry Context is the time keeper and an accountant: its responsible for
maintaining the delay value and the retry count.


.. code-block:: python
   :caption: Limited number of tries (iterations)

   >>> from kaioretry import Context
   >>> context = Context(tries=4)
   >>> for i, _ in enumerate(context):
   ...    print(i)
   ...
   0
   1
   2
   3
   >>> 


Should you wish to persist indefinitely. It is supported.

.. code-block:: python
   :caption: Unlimited number of tries (iterations)

   >>> from kaioretry import Context
   >>> context = Context(tries=-1)
   >>> for i, _ in enumerate(context):
   ...    print(i)
   ...
   0
   1
   2
   ... there it goes
   30
   31...
   .... and so on
   25000
   .................
   # It never stops.


It's possible to insert delay between tries.


.. code-block:: python
   :caption: Adding a one second delay between tries.

   >>> from kaioretry import Context
   >>> context = Context(tries=4, delay=1)
   >>> for i, _ in enumerate(context):
   ...     print(time())
   ...
   1677350589.3510618
   1677350590.3776977
   1677350591.403194
   1677350592.429291
   >>> 


It will also log its actions and will help keep things being traceable by
adding a per-loop identifier to the logs. e.g:

.. code-block:: python
   :caption: logging loops

   >>> import sys, logging
   >>> logging.basicConfig(stream=sys.stdout, encoding='utf-8', level=logging.DEBUG)
   >>> from kaioretry import Context
   >>> for _ in context: pass
   ... 
   INFO:kaioretry.context:00cc19af-7339-442f-9804-16eb10788068: 2 tries remaining
   INFO:kaioretry.context:00cc19af-7339-442f-9804-16eb10788068: sleeping 0 seconds
   INFO:kaioretry.context:00cc19af-7339-442f-9804-16eb10788068: 1 tries remaining
   INFO:kaioretry.context:00cc19af-7339-442f-9804-16eb10788068: sleeping 0 seconds
   >>> for _ in context: pass
   ... 
   INFO:kaioretry.context:1c4ddbdb-f2b0-4377-a840-92ea8c651ac1: 2 tries remaining
   INFO:kaioretry.context:1c4ddbdb-f2b0-4377-a840-92ea8c651ac1: sleeping 0 seconds
   INFO:kaioretry.context:1c4ddbdb-f2b0-4377-a840-92ea8c651ac1: 1 tries remaining
   INFO:kaioretry.context:1c4ddbdb-f2b0-4377-a840-92ea8c651ac1: sleeping 0 seconds
   >>> 

If you consider this from :py:class:`~kaioretry.Retry` point of view, it means
that you can keep track of calls, delays and number of tries per calls.

If you want to do more fine tuning to delays and tries, check the
documentation below.

"""

import time
import asyncio
import logging
import uuid

from typing import cast, Awaitable, Any, TypeVar, Generic
from collections.abc import Callable, Generator, AsyncGenerator

from .types import NonNegative, Number, UpdateDelayFunc


SleepRetVal = TypeVar('SleepRetVal', None, Awaitable[None])
SleepF = Callable[[Number], SleepRetVal]


class _ContextIterator(Generic[SleepRetVal]):
    """Single-usage helper class for Context objects."""

    # pylint: disable=too-few-public-methods

    def __init__(self, identifier: uuid.UUID, sleep: SleepF[Any], tries: int,
                 delay: NonNegative, update_delay: UpdateDelayFunc,
                 logger: logging.Logger, /) -> None:
        # pylint: disable=too-many-arguments
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

    :param update_delay: a function that will produce the next value of delay
        value. Can be anything as long as it produces a positive number when
        called.

    :param max_delay: the maximum value allowed for delay. If None
        (the default), then delay is unlimited. Cannot be negative.

    :param min_delay: the minimum value allowed for delay. Cannot be
        negative. Default is 0.

    :param logger: the :py:class:`logging.Logger` object to which the
        log messages will be sent to.

    :raises ValueError: if tries, min_delay or max_delay have incorrect values.

    """

    DEFAULT_LOGGER: logging.Logger = logging.getLogger(__name__)
    """The :py:class:`logging.Logger` object that will be used if none
    are provided to the constructor.
    """

    def __init__(self, /, tries: int = -1, delay: NonNegative = 0, *,
                 update_delay: UpdateDelayFunc = lambda value: value,
                 max_delay: NonNegative | None = None,
                 min_delay: NonNegative = 0,
                 logger: logging.Logger = DEFAULT_LOGGER) -> None:
        # pylint: disable=too-many-arguments
        if tries == 0:
            raise ValueError("tries value cannot be 0")
        self.__tries = tries
        self.__delay = delay
        self.__update_delay_value = update_delay
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
            f"delay=({min_delay}<={delay}<={max_delay}))")
        self.__logger = logger

    def __update_delay(self, delay: NonNegative) -> NonNegative:
        """Compute the updated values for given delay.

        :param delay: the current value of delay between iterations.

        :returns: the new duration to wait for before the next iteration.
        """
        delay = self.__update_delay_value(delay)
        if self.__max_delay is not None:
            delay = min(delay, self.__max_delay)
        delay = max(delay, self.__min_delay)
        return delay

    def __make_iterator(
            self, sleep: SleepF[SleepRetVal]) -> Generator[SleepRetVal, None, None]:
        return iter(_ContextIterator(
            uuid.uuid4(), sleep, self.__tries, self.__delay,
            self.__update_delay, self.__logger))

    def __iter__(self) -> Generator[None, None, None]:
        yield
        yield from self.__make_iterator(time.sleep)

    async def __aiter__(self) -> AsyncGenerator[None, None]:
        yield
        for sleep in self.__make_iterator(asyncio.sleep):
            await sleep
            yield

    def __str__(self) -> str:
        return self.__str


__all__ = ['Context']
