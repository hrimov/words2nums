import abc
from typing import List, Protocol

from words2nums.core.types import NumberData


class Parser(Protocol):
    @abc.abstractmethod
    def parse(self, tokens: List[str]) -> NumberData: ...
