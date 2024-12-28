import abc
from typing import Protocol

from words2nums.core.types import (
    NumberData,
    ReturnValue,
)


class Evaluator(Protocol):
    @abc.abstractmethod
    def evaluate(self, data: NumberData) -> ReturnValue: ...
