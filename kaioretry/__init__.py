"""Retry decorator to automatically call a function again on errors"""

import logging
import random

from typing import cast
from collections.abc import Callable
from mypy_extensions import DefaultNamedArg, DefaultArg

from .types import Exceptions, NonNegative, Number, Jitter, \
    FuncParam, FuncRetVal, UpdateDelayFunc, JitterTuple, AioretryProtocol
from .context import Context
from .decorator import Retry


__version__ = "0.12.0"


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
    :raises TypeError: if jitter is neither a Number nor a :py:class:`tuple`.
"""


def _make_decorator(func: Callable[[Retry], Callable[FuncParam, FuncRetVal]]) \
    -> Callable[[
        DefaultArg(Exceptions, 'exceptions'),  # noqa: F821
        DefaultArg(int, 'tries'),              # noqa: F821
        DefaultNamedArg(NonNegative, 'delay'),  # noqa: F821
        DefaultNamedArg(Number, 'backoff'),  # noqa: F821
        DefaultNamedArg(Jitter, 'jitter'),  # noqa: F821
        DefaultNamedArg(NonNegative | None, 'max_delay'),  # noqa: F821
        DefaultNamedArg(NonNegative, 'min_delay'),  # noqa: F821
        DefaultNamedArg(logging.Logger, 'logger')],  # noqa: F821
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

        if isinstance(jitter, (int, float)):
            jitter_f = cast(UpdateDelayFunc, jitter.__add__)
        elif isinstance(jitter, (tuple, list)):
            def jitter_f(delay: Number) -> Number:
                return random.uniform(*cast(JitterTuple, jitter)) + delay
        else:
            raise TypeError("jitter parameter is neither a number "
                            f"nor a 2 length tuple: {jitter}")

        def update_delay(delay: NonNegative) -> NonNegative:
            return jitter_f(delay * backoff)

        context = Context(
            tries=tries, delay=delay, update_delay=update_delay,
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
    """Return a new retry decorator, suitable for regular functions. Functions
    decorated will transparently retry when a exception is raised.

    %PARAMS%

    :returns: a retry decorator for regular (non-coroutine) functions.

    """
    return retry_obj.retry


@_make_decorator
def aioretry(retry_obj: Retry) -> AioretryProtocol:
    """Similar to :py:func:`~kaioretry.retry`, this function will produce
    a new async retry decorator that will produce exact the same
    results as said :py:func:`~kaioretry.retry`, *except* that the
    produced decorated functions will be typed as a
    :py:class:`~collections.abc.Coroutine`, and that delays induced by
    the `delay` constructor parameter and its friends, will be
    implemented with :py:mod:`asyncio` functions.

    That means the decorated version of given functions will be eligible to
    :py:func:`asyncio.run` or to an `await` statement, even if given `func`
    parameter is not originally an async function to begin with.

    %PARAMS%

    :returns: a retry decorator that generates coroutines functions.

    """
    return retry_obj.aioretry


__all__ = ['Retry', 'Context', 'retry', 'aioretry']
