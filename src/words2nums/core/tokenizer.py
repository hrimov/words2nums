import abc
from typing import List, Protocol


class Tokenizer(Protocol):
    @abc.abstractmethod
    def tokenize(self, text: str) -> List[str]: ...
