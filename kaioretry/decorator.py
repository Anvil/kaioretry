"""The retry decorator implementation"""

import asyncio
import inspect
import logging

from typing import Callable, Awaitable, cast, Any, NoReturn

import decorator

from .types import Exceptions, ExceptionList, FuncParam, FuncRetVal, Function
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

    DEFAULT_LOGGER = logging.getLogger(__name__)

    DEFAULT_CONTEXT = Context(tries=-1, delay=0)

    def __init__(
            self, /, exceptions: Exceptions = Exception, *,
            context: Context = DEFAULT_CONTEXT,
            logger: logging.Logger = DEFAULT_LOGGER) -> None:
        self.__exceptions = exceptions
        self.__context = context
        self.__logger = logger
        if isinstance(exceptions, type(BaseException)):
            exc_str = exceptions.__name__
        else:
            exc_str = ", ".join(
                exception.__name__
                for exception in cast(ExceptionList, exceptions))
        self.__str = f"{self.__class__.__name__}({exc_str}, {context})"

    def __log(self, level: int, fmt: str, *args: Any) -> None:
        self.__logger.log(level, f"{self}: {fmt}", *args)

    def __caught_error(self, func: Function, error: BaseException) -> None:
        self.__log(
            logging.WARN, "%s caught while running %s: %s.",
            error.__class__.__name__, func.__name__, error)

    def __final_error(self, func: Function, error: BaseException) -> NoReturn:
        self.__log(logging.WARN, "%s failed to complete", func.__name__)
        raise error

    def __success(self, func: Function) -> None:
        self.__log(
            logging.INFO, "%s has succesfully completed", func.__name__)

    # pylint: disable=inconsistent-return-statements
    def __retry(self, func: Callable[FuncParam, FuncRetVal],
                *args: FuncParam.args,
                **kwargs: FuncParam.kwargs) -> FuncRetVal:
        for _ in self.__context:
            try:
                result = func(*args, **kwargs)
                self.__success(func)
                return result
            # It does not matter if it's broad :p this is user
            # configuration.
            # pylint: disable=broad-except
            except self.__exceptions as error:
                self.__caught_error(func, error)
                last_error = error
                continue
        self.__final_error(func, last_error)

    def retry(self, func: Callable[FuncParam, FuncRetVal]) \
        -> Callable[FuncParam, FuncRetVal]:
        """Decorate a regular function.

        The decoration will retry the original function every time it
        raises an exception, until number of tries from the context
        are exhausted.
        """
        return decorator.decorate(func, self.__retry)

    async def __aioretry(
            self,
            func: Callable[FuncParam, Awaitable[FuncRetVal]] | Callable[FuncParam, FuncRetVal],
            *args: FuncParam.args,
            **kwargs: FuncParam.kwargs) -> FuncRetVal:
        async for _ in self.__context:
            try:
                result = func(*args, **kwargs)
                if inspect.isawaitable(result):
                    result = await result
                self.__success(func)
                return cast(FuncRetVal, result)
            # pylint: disable=broad-except
            except self.__exceptions as error:
                self.__caught_error(func, error)
                last_error = error
                continue
        self.__final_error(func, last_error)

    def aioretry(
            self,
            func: Callable[FuncParam, Awaitable[FuncRetVal]] | Callable[FuncParam, FuncRetVal]) \
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
        return cast(Callable[FuncParam, Awaitable[FuncRetVal]],
                    decorator.decorate(func, self.__aioretry))

    def __call__(
            self, func: Callable[FuncParam, FuncRetVal] |
            Callable[FuncParam, Awaitable[FuncRetVal]]) \
        -> Callable[FuncParam, FuncRetVal] | Callable[FuncParam, Awaitable[FuncRetVal]]:
        if asyncio.iscoroutinefunction(func):
            return cast(Callable[FuncParam, Awaitable[FuncRetVal]], self.aioretry(func))
        return cast(Callable[FuncParam, FuncRetVal], self.retry(func))

    def __str__(self) -> str:
        return self.__str
