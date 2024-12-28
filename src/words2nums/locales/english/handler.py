from words2nums.core.evaluator import Evaluator
from words2nums.core.handler import Handler, HandlerFactory
from words2nums.core.parser import Parser
from words2nums.core.tokenizer import Tokenizer
from words2nums.locales.english.evaluator import EnglishEvaluator
from words2nums.locales.english.parser import EnglishParser
from words2nums.locales.english.tokenizer import EnglishTokenizer


class EnglishHandlerFactory(HandlerFactory):
    def create_tokenizer(self) -> Tokenizer:
        return EnglishTokenizer()

    def create_parser(self) -> Parser:
        return EnglishParser()

    def create_evaluator(self) -> Evaluator:
        return EnglishEvaluator()


class EnglishHandler(Handler):
    @classmethod
    def create_factory(cls) -> HandlerFactory:
        return EnglishHandlerFactory()
