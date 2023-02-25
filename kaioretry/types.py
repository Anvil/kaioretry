"""Custom types used by kaioretry"""


from logging import Logger, getLogger
from typing import TypeAlias, TypeVar, ParamSpec, Any
from collections.abc import Callable

from typing_extensions import Protocol

# Protocols do not have public methods. This module will not define any
# otherwise valid class.
# pylint: disable=too-few-public-methods


ExceptionT: TypeAlias = type[BaseException]
ExceptionList: TypeAlias = tuple[ExceptionT, ...]
Exceptions: TypeAlias = ExceptionList | ExceptionT


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


UpdateDelayF: TypeAlias = Callable[[NonNegative], NonNegative]


class RetryDecorator(Protocol):
    """Retry Decorator Type"""
    def __call__(self,
                 exceptions: Exceptions = Exception, tries: int = -1, *,
                 delay: NonNegative = 0, backoff: Number = 1,
                 jitter: Jitter = 0,  max_delay: NonNegative | None = None,
                 min_delay: NonNegative = 0,
                 logger: Logger = getLogger(__name__)) \
            -> Callable[FuncParam, FuncRetVal]:
        ...                     # pragma: nocover
