from abc import ABC, abstractmethod

from words2nums.core.tokenizer import Tokenizer
from words2nums.core.parser import Parser
from words2nums.core.evaluator import Evaluator
from words2nums.core.types import ReturnValue


class HandlerFactory(ABC):
    """Abstract factory for creating complete handler component families"""

    @abstractmethod
    def create_tokenizer(self) -> Tokenizer:
        """Create a tokenizer handler component"""
        pass

    @abstractmethod
    def create_parser(self) -> Parser:
        """Create a parser handler component"""
        pass

    @abstractmethod
    def create_evaluator(self) -> Evaluator:
        """Create a evaluator handler component"""
        pass


class Handler(ABC):
    @classmethod
    @abstractmethod
    def create_factory(cls) -> HandlerFactory:
        """Create the appropriate factory for this handler"""
        raise NotImplementedError

    @classmethod
    def create_default(cls) -> "Handler":
        """Create a handler with default components"""
        factory = cls.create_factory()
        tokenizer = factory.create_tokenizer()
        parser = factory.create_parser()
        evaluator = factory.create_evaluator()
        return cls(tokenizer, parser, evaluator)

    def __init__(
            self,
            tokenizer: Tokenizer,
            parser: Parser,
            evaluator: Evaluator
    ) -> None:
        self._tokenizer = tokenizer
        self._parser = parser
        self._evaluator = evaluator

    def convert(self, text: str) -> ReturnValue:
        tokens = self._tokenizer.tokenize(text)
        tree = self._parser.parse(tokens)
        result = self._evaluator.evaluate(tree)
        return result
