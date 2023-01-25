"""The retry decorator implementation"""

import asyncio
import inspect

from typing import Callable, Awaitable, cast

from .types import Exceptions, FuncParam, FuncRetVal
from .context import Context


class Retry:

    """Objects of the Retry class are retry decorators.

    They can decorate both functions and coroutine functions. Every
    time the decorated function is called and raises an error, it will
    automatically be retried until the number of tries is exhausted.

    Functions can either be decorated by the retry method, the
    aioretry method, or by the object itself. If the object is used as
    decorator, an heuristic will attempt to determine what is the best
    alternative (retry or aioretry), depending of the nature of the
    function and the context of a event loop.

    :param exceptions: exceptions classes that will trigger another
        try. Other exceptions raised by the decorated function will
        not trigger a retry. The value of the exceptions parameters
        can be eiher an Exception or a tuple of Exception or whatever
        is suitable for an except clause. The default is the Exception
        class, which means any error will trigger a new try.

    :param context: a Context object that will be used to maintain try
        count and the delay between them. If omitted, a Context with
        an inifite unmber of tries and no delay betwen them will be
        used.

    """

    DEFAULT_CONTEXT = Context(tries=-1, delay=0)

    def __init__(
            self, /, exceptions: Exceptions = Exception, *,
            context: Context = DEFAULT_CONTEXT) -> None:
        self.__exceptions = exceptions
        self.__context = context

    def retry(self, func: Callable[FuncParam, FuncRetVal]) \
        -> Callable[FuncParam, FuncRetVal]:
        """Decorate a regular function.

        The decoration will retry the original function every time it
        raises an exception, until number of tries from the context
        are exhausted.
        """
        def _decorated(*args: FuncParam.args,
                       **kwargs: FuncParam.kwargs) -> FuncRetVal:
            for _ in self.__context:
                try:
                    return func(*args, **kwargs)
                # It does not matter if it's broad :p this is user
                # configuration.
                # pylint: disable=broad-except
                except self.__exceptions as error:
                    last_error = error
                    continue
            raise last_error

        return _decorated

    def aioretry(
            self,
            func: Callable[FuncParam, Awaitable[FuncRetVal] | FuncRetVal]) \
            -> Callable[FuncParam, Awaitable[FuncRetVal]]:
        """Decorate a function with an async retry decoration.

        Given function can either be a coroutine function, a regular
        function, or a regular function returning an awaitable
        object. If its result is an awaitable object, then it will be
        awaited by the decoration before being returned.

        :param func: any callable.

        :returns: an async function that will return the same result
            as the original function's

        """
        async def _decorated(
                *args: FuncParam.args, **kwargs: FuncParam.kwargs) \
                -> FuncRetVal:
            async for _ in self.__context:
                try:
                    result = func(*args, **kwargs)
                    if inspect.isawaitable(result):
                        result = await result
                    return cast(FuncRetVal, result)
                # pylint: disable=broad-except
                except self.__exceptions as error:
                    last_error = error
                    continue
            raise last_error

        return _decorated

    def __call__(self, func: Callable[FuncParam, FuncRetVal]) \
        -> Callable[FuncParam, FuncRetVal]:
        if asyncio.iscoroutinefunction(func):
            return cast(Callable[FuncParam, FuncRetVal], self.aioretry(func))
        return self.retry(func)
