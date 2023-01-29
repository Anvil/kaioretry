"""Retry decorator to automatically call a function again on errors"""

from typing import Optional, Callable, Awaitable, Union

from .types import Exceptions, NonNegative, Number, Jitter, FuncParam, FuncRetVal
from .context import Context
from .decorator import Retry


__version__ = "0.3.0"


RETRY_PARAMS_DOCSTRING = """

    :param exceptions: exceptions classes that will trigger another
        try. Other exceptions raised by the decorated function will
        not trigger a retry. The value of the exceptions parameters
        can be eiher an Exception or a tuple of Exception (actually,
        whatever is suitable for an except clause). The default is the
        Exception class, which means any error will trigger a new try.

    :param delay: the initial number of seconds to wait between two
        iterations. It must be non-negative. Default is 0.

    :param backoff: a multiplier applied to delay after each
        iteration. It can be a float, and it can actually be less than
        one. Default: 1 (no backoff).

    :param jitter: extra seconds added to delay between
        iterations. Default: 0.

    :param jitter: extra seconds added to delay between attempts. default: 0.
                   fixed if a number, random if a range tuple (min, max)
    :param max_delay: the maximum value of delay. default: None (no limit).

    :returns: a retry decorator for regular (non-coroutine) functions.
"""


# pylint: disable=too-many-arguments


def retry(
        exceptions: Exceptions = Exception, tries: int = -1,
        delay: NonNegative = 0, backoff: Number = 1,
        jitter: Jitter = 0,  max_delay: NonNegative | None = None,
        min_delay: NonNegative = 0) -> Callable[
            [Callable[FuncParam, FuncRetVal]],
            Callable[FuncParam, FuncRetVal]]:
    """Returns a retry decorator, suitable for regular functions."""
    context = Context(
        tries=tries, delay=delay, backoff=backoff, jitter=jitter,
        max_delay=max_delay, min_delay=min_delay)
    return Retry(exceptions=exceptions, context=context).retry


def aioretry(
        exceptions: Exceptions = Exception, tries: int = -1,
        delay: NonNegative = 0, backoff: Number = 1,
        jitter: Jitter = 0,  max_delay: NonNegative | None = None,
        min_delay: NonNegative = 0) -> Callable[
            [Callable[FuncParam, FuncRetVal] | Callable[FuncParam, Awaitable[FuncRetVal]]],
            Callable[FuncParam, Awaitable[FuncRetVal]]]:
    # pylint: disable=too-many-arguments
    """Returns a retry decorator, suitable for coroutine functions."""
    context = Context(
        tries=tries, delay=delay, backoff=backoff, jitter=jitter,
        max_delay=max_delay, min_delay=min_delay)
    return Retry(exceptions=exceptions, context=context).aioretry


for func in [retry, aioretry]:  # pragma: nocover
    if func.__doc__ is not None:
        func.__doc__ += RETRY_PARAMS_DOCSTRING


__all__ = ['Retry', 'Context', 'retry']
