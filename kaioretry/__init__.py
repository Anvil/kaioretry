"""Retry decorator to automatically call a function again on errors"""

import logging
from typing import Awaitable
from collections.abc import Callable

from .types import Exceptions, NonNegative, Number, Jitter, \
    FuncParam, FuncRetVal
from .context import Context
from .decorator import Retry


__version__ = "0.8.4"


RETRY_PARAMS_DOCSTRING = """
    :param exceptions: exceptions classes that will trigger another
        try. Other exceptions raised by the decorated function will
        not trigger a retry. The value of the exceptions parameters
        can be either an :py:class:`Exception` class or a
        :py:class:`tuple` of :py:class:`Exception` classes (actually,
        whatever is suitable for an except clause). The default is the
        :py:class:`Exception` class, which means any error will
        trigger a new try.

    :param tries: the maximum number of iterations (a.k.a.: tries,
        function calls) to perform before exhaustion. A negative value
        means infinite. 0 is forbidden, since it would mean "don't
        run" at all.

    :param delay: the initial number of seconds to wait between two
        iterations. It must be non-negative. Default is 0.

    :param backoff: a multiplier applied to delay after each
        iteration. It can be a float, and it can actually be less than
        one. Default: 1 (no backoff).

    :param jitter: extra seconds added to delay between
        iterations. Default: 0.

    :param max_delay: the maximum value of delay. default: None (no limit).

    :param min_delay: the minimum value allowed for delay. Cannot be
        negative. Default is 0.

    :param logger: the :py:class:`logging.Logger` object to which the
        log messages will be sent to.

    :raises ValueError: if tries, min_delay or max_delay have incorrect values.
    :raises TypeError: if jitter is neither a Number or a tuple.
"""


def _make_decorator(func: Callable[[Retry], Callable[FuncParam, FuncRetVal]]) \
    -> Callable[[Exceptions, int, NonNegative, Number, Jitter,
                 NonNegative | None, NonNegative, logging.Logger],
                Callable[FuncParam, FuncRetVal]]:
    """Create a function that will accept a bunch of parameters and
    create the matching :py:class:`Retry` and :py:class:`Context`
    objects, in order to be compatible with the origin retry module.

    This function avoids the duplication and double maintenance of
    :py:func:`retry` and :py:func:`aioretry` signatures.

    :param func: a function that takes a :py:class:`Retry` object as
        parameter and provides a decorator as a result.

    :returns: a new function that accepts what is basically the
        union-set of Retry and Context constructors.

    """
    # pylint: disable=too-many-arguments
    def decoration(
            exceptions: Exceptions = Exception, tries: int = -1, *,
            delay: NonNegative = 0, backoff: Number = 1,
            jitter: Jitter = 0,  max_delay: NonNegative | None = None,
            min_delay: NonNegative = 0,
            logger: logging.Logger = Retry.DEFAULT_LOGGER) \
            -> Callable[FuncParam, FuncRetVal]:
        context = Context(
            tries=tries, delay=delay, backoff=backoff, jitter=jitter,
            max_delay=max_delay, min_delay=min_delay, logger=logger)
        retry_obj = Retry(
            exceptions=exceptions, context=context, logger=logger)
        return func(retry_obj)

    if func.__doc__ is not None:  # pragma: nocover
        decoration.__doc__ = func.__doc__.replace(
            "%PARAMS%", RETRY_PARAMS_DOCSTRING)
    return decoration


@_make_decorator
def retry(retry_obj: Retry) -> Callable[[Callable[FuncParam, FuncRetVal]],
                                        Callable[FuncParam, FuncRetVal]]:
    """Returns a retry decorator, suitable for regular functions.

    %PARAMS%

    :returns: a retry decorator for regular (non-coroutine) functions.

    """
    return retry_obj.retry


@_make_decorator
def aioretry(retry_obj: Retry) -> Callable[
        [Callable[FuncParam, FuncRetVal] |
         Callable[FuncParam, Awaitable[FuncRetVal]]],
        Callable[FuncParam, Awaitable[FuncRetVal]]]:
    """Returns a retry decorator, suitable for both regular functions
    and coroutine functions. The decoration will turn the original
    function to a coroutine function.

    %PARAMS%

    :returns: a retry decorator that generates coroutines functions.

    """
    return retry_obj.aioretry


__all__ = ['Retry', 'Context', 'retry', 'aioretry']
