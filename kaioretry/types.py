"""Custom types used by kaioretry"""


from typing import TypeAlias, TypeVar, ParamSpec, Any
from collections.abc import Callable


ExceptionT: TypeAlias = type[BaseException]
ExceptionList: TypeAlias = tuple[ExceptionT, ...]
Exceptions: TypeAlias = ExceptionList | ExceptionT


Number: TypeAlias = int | float


# Until better implementation.
NonNegative: TypeAlias = Number   # >= 0
Positive: TypeAlias = Number      # >  0


# jitter parameter type is a bit specific
Jitter: TypeAlias = Number | tuple[Number, Number]


FuncParam = ParamSpec('FuncParam')
FuncRetVal = TypeVar('FuncRetVal')

Function: TypeAlias = Callable[..., Any]
