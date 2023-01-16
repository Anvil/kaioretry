"""Custom types used by kaioretry"""


from typing import Union, Type, TypeAlias, TypeVar, ParamSpec


Exceptions: TypeAlias = tuple[Type[BaseException], ...] | Type[BaseException]


Number: TypeAlias = int | float


# Until better implementation.
NonNegative: TypeAlias = Number   # >= 0
Positive: TypeAlias = Number      # >  0


# jitter parameter type is a bit specific
Jitter: TypeAlias = Union[Number, tuple[Number, Number]]


FuncParam = ParamSpec('FuncParam')
FuncRetVal = TypeVar('FuncRetVal')
