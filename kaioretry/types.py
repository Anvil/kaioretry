"""Kaioretry helper types"""


from typing import TypeAlias, TypeVar, ParamSpec, Any, overload
from collections.abc import Callable, Coroutine, Awaitable

from typing_extensions import Protocol

# Protocols do not have public methods. This module will not define any
# otherwise valid class.
# pylint: disable=too-few-public-methods


ExceptionType: TypeAlias = type[BaseException]
ExceptionList: TypeAlias = tuple[ExceptionType, ...]
Exceptions: TypeAlias = ExceptionList | ExceptionType


Number: TypeAlias = int | float


# Until better implementation.
NonNegative: TypeAlias = Number   # >= 0
Positive: TypeAlias = Number      # >  0


# jitter parameter type is a bit specific
JitterTuple: TypeAlias = tuple[Number, Number]
Jitter: TypeAlias = Number | JitterTuple


FuncParam = ParamSpec('FuncParam')

FuncRetVal = TypeVar('FuncRetVal')

Function: TypeAlias = Callable[..., Any]

UpdateDelayFunc: TypeAlias = Callable[[NonNegative], NonNegative]


AioretryCoro: TypeAlias = Callable[
    FuncParam, Coroutine[None, None, FuncRetVal]]

AwaitableFunc: TypeAlias = Callable[FuncParam, Awaitable[FuncRetVal]]

AnyFunction: TypeAlias = AwaitableFunc[FuncParam, FuncRetVal] | \
    Callable[FuncParam, FuncRetVal]

class AioretryProtocol(Protocol):

    """The :py:class:`typing.Protocol` describing the behaviour of the
    :py:func:`~kaioretry.aioretry` decorator.

    .. automethod:: __call__
    """

    @overload
    def __call__(self, func: AwaitableFunc[FuncParam, FuncRetVal]) \
            -> AioretryCoro[FuncParam, FuncRetVal]:
        ...

    @overload
    def __call__(self, func: Callable[FuncParam, FuncRetVal]) \
            -> AioretryCoro[FuncParam, FuncRetVal]:
        ...

    def __call__(self, func: AnyFunction[FuncParam, FuncRetVal]) \
            -> AioretryCoro[FuncParam, FuncRetVal]:
        """When called (to decorate a function), an aioretry decorator will...

        :param func: ... take a function as input...

        :returns: ... and,

            * if ``func`` returns an :py:class:`~collections.abc.Awaitable`,
              then return a same-signature same-type coroutine function.
            * If ``func`` does not, then return a same-signature *coroutine* function
              that, once awaited, return ``func`` original return value.
        """
