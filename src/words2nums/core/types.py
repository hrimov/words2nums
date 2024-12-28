from abc import ABC
from typing import Type, TypeAlias


ReturnValue: TypeAlias = int | float
# Note: consider to remove it
# as for now we don't need it at all (due to `as_type` removal)
ReturnValueType: TypeAlias = Type[ReturnValue]


class NumberData(ABC):
    pass
