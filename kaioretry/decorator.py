"""Not considering the 2 main functions :py:func:`kaioretry.retry` and
:py:func:`kaioretry.aioretry` decorators, KaioRetry is basically split in two
main classes, with shared responsabilities:

* :py:class:`~kaioretry.Retry` is in charge of handling the decoration and the
  retry process;

* and :py:class:`~kaioretry.Context` is in charge of keeping track of the try
  count and delaying management.


.. code-block:: python
   :caption: The object can be used to decorate either regular or coroutine
             function.

   from kaioretry import Retry

   retry = Retry(ValueError)

   @retry
   def something_we_dont_wanna_see_crashing():
       ...

   @retry
   async def some_async_thing_we_dont_wanna_see_crashing():
       # The decorated version of this function will still be async
       ...



.. code-block:: python
   :caption: You can also use the object methods to explicitly decorate as
             regular or coroutine function.

   from kaioretry import Retry

   retry = Retry(ValueError)

   # On one hand, the retry method produces regular functions.
   @retry.retry
   def something_we_dont_wanna_see_crashing():
       ...

   # On the other hand, the aioretry method produces coroutine functions.
   @retry.aioretry
   async def some_async_thing_we_dont_wanna_see_crashing():
       # The decorated version of this function will still be async
       ...

   # From a KaioRetry point of view, you can use aioretry to decorate a
   # regular function to produce a coroutine function. It's designed to work.
   @retry.aioretry
   def something_regular():
       ...



To refine the number of tries, or delay between said tries. You must use a
:py:class:`~kaioretry.Context` object and give it to
:py:class:`~kaioretry.Retry` constructor.

.. code-block:: python
   :caption: Use and pass a Context object

   from kaioretry import Context, Retry

   context = Context(tries=3, delay=1)

   @Retry(ValueError, context=context)
   def genkidama(...):
       ...


Check out the classes documentation and attributes for more fine tuning.

"""

import inspect
import logging

from collections.abc import Callable, Awaitable, Coroutine
from typing import cast, Any, NoReturn, Awaitable as OldAwaitable, overload

import decorator

from .types import Exceptions, ExceptionList, FuncParam, FuncRetVal, Function
from .context import Context


class Retry:

    """Objects of the Retry class are retry decorators.

    They can decorate both functions and coroutine functions. Every
    time the decorated function is called and raises an error, it will
    automatically be retried until the number of tries is exhausted.

    Functions can either be decorated by the retry method, the
    aioretry method, or by the object itself. If the object sed as
    decorator, an heuristic will attempt to determine what is the best
    alternative (retry or aioretry), depending of the nature of the
    function and the context of a event loop.

    :param exceptions: :py:class:`Exception` classes that will trigger
        another try. Other exceptions raised by the decorated function
        will not trigger a retry. The value of the exceptions
        parameters can be either an :py:class:`Exception` class or a
        :py:class:`tuple` of :py:class:`Exception` classes or whatever
        is suitable for an except clause. The default is the
        :py:class:`Exception` class, which means any error will
        trigger a new try.

    :param context: a :py:class:`~kaioretry.context.Context` object
        that will be used to maintain try count and the delay between
        them. If omitted, a :py:class:`~kaioretry.context.Context`
        with an infinite nunmber of tries and no delay betwen them
        will be used.

    :param logger: the :py:class:`logging.Logger` to which the log
        messages will be sent to.

    """

    DEFAULT_LOGGER: logging.Logger = logging.getLogger(__name__)
    """The :py:class:`logging.Logger` object that will be used if none
    are provided to the constructor.
    """

    DEFAULT_CONTEXT: Context = Context(tries=-1, delay=0)
    """A default :py:class:`~kaioretry.context.Context` that will be
    used if none are provided to the constructor.

    It will provide an infinity of tries with no delay between them.
    """

    def __init__(
            self, /, exceptions: Exceptions = Exception,
            context: Context = DEFAULT_CONTEXT, *,
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
            func: Callable[FuncParam, Awaitable[FuncRetVal]] |
            Callable[FuncParam, FuncRetVal],
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

    @overload
    def aioretry(self, func: Callable[FuncParam, Awaitable[FuncRetVal]]) \
            -> Callable[FuncParam, Coroutine[None, None, FuncRetVal]]:
        ...

    @overload
    def aioretry(self, func: Callable[FuncParam, FuncRetVal]) \
            -> Callable[FuncParam, Coroutine[None, None, FuncRetVal]]:
        ...

    def aioretry(
            self,
            func: Callable[FuncParam, Awaitable[FuncRetVal]] |
            Callable[FuncParam, FuncRetVal]) \
            -> Callable[FuncParam, Coroutine[None, None, FuncRetVal]]:
        """Decorate a function with an async retry decoration.

        Given function can either be a coroutine function, a regular
        function, or a regular function returning an awaitable
        object. If its result is an awaitable object, then it will be
        awaited by the decoration before being returned.

        :param func: any callable.

        :returns: an async function that will return the same result
            as the original function's

        """
        return cast(Callable[FuncParam, Coroutine[None, None, FuncRetVal]],
                    decorator.decorate(func, self.__aioretry))

    __is_not_async_type = {Awaitable, OldAwaitable}.isdisjoint

    @classmethod
    def _has_async_return_annotation(cls, func: Function) -> bool:
        """Tell if a function is annotated to return an
        async-ish type.

        :param func: any callable

        :returns: True if return type annotation is either Awaitable,
            AsyncGenerator, or their variant.

        """
        try:
            rtype = func.__annotations__['return']
        except (AttributeError, KeyError):
            return False
        try:
            origin = rtype.__origin__
        except AttributeError:
            origin = rtype
        return not cls.__is_not_async_type({rtype, origin})

    @classmethod
    def is_func_async(cls, func: Function) -> bool:
        """Tell if a function can be considered async, either because
        it's a coroutine, an asyncgenerator or because it's annotated
        to return :py:class:`collections.abc.Awaitable` or
        :py:class:`typing.Awaitable`.
        """
        return inspect.iscoroutinefunction(func) or \
            cls._has_async_return_annotation(func)

    def __call__(self, func: Callable[FuncParam, FuncRetVal]) \
            -> Callable[FuncParam, FuncRetVal]:
        if self.is_func_async(func):
            return self.aioretry(
                cast(Callable[FuncParam, Awaitable[Any]], func))
        return self.retry(func)

    def __str__(self) -> str:
        return self.__str


__all__ = ['Retry']
