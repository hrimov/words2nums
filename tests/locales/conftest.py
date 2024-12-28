import pytest
from words2nums import Converter
from words2nums.locales.english.tokenizer import EnglishTokenizer


@pytest.fixture
def converter():
    return Converter()


@pytest.fixture
def tokenizer():
    return EnglishTokenizer()
