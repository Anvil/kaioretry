"""Custom types used by kaioretry"""


from typing import Union, Type, TypeAlias, TypeVar, ParamSpec, Callable, Any


ExceptionT: TypeAlias = Type[BaseException]
ExceptionList: TypeAlias = tuple[ExceptionT, ...]
Exceptions: TypeAlias = ExceptionList | ExceptionT


Number: TypeAlias = int | float


# Until better implementation.
NonNegative: TypeAlias = Number   # >= 0
Positive: TypeAlias = Number      # >  0


# jitter parameter type is a bit specific
Jitter: TypeAlias = Union[Number, tuple[Number, Number]]


FuncParam = ParamSpec('FuncParam')
FuncRetVal = TypeVar('FuncRetVal')

Function: TypeAlias = Callable[..., Any]
