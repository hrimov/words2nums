import pytest
from words2nums.locales.english.parser import EnglishParser
from words2nums.core.exceptions import ParsingError


@pytest.fixture
def parser():
    return EnglishParser()


def test_basic_numbers(parser):
    # Test single digits
    assert parser.parse(["zero"]).evaluate() == 0
    assert parser.parse(["one"]).evaluate() == 1
    assert parser.parse(["nine"]).evaluate() == 9
    
    # Test teens
    assert parser.parse(["eleven"]).evaluate() == 11
    assert parser.parse(["fifteen"]).evaluate() == 15
    assert parser.parse(["nineteen"]).evaluate() == 19
    
    # Test tens
    assert parser.parse(["twenty"]).evaluate() == 20
    assert parser.parse(["fifty"]).evaluate() == 50
    assert parser.parse(["ninety"]).evaluate() == 90
    
    # Test compound numbers
    assert parser.parse(["twenty", "one"]).evaluate() == 21
    assert parser.parse(["forty", "five"]).evaluate() == 45
    assert parser.parse(["ninety", "nine"]).evaluate() == 99


def test_hundreds(parser):
    assert parser.parse(["one", "hundred"]).evaluate() == 100
    assert parser.parse(["five", "hundred"]).evaluate() == 500
    assert parser.parse(["nine", "hundred"]).evaluate() == 900
    
    # Test with additional tens/ones
    assert parser.parse(["one", "hundred", "one"]).evaluate() == 101
    assert parser.parse(["two", "hundred", "twenty"]).evaluate() == 220
    assert parser.parse(["five", "hundred", "fifty", "five"]).evaluate() == 555


def test_thousands(parser):
    assert parser.parse(["one", "thousand"]).evaluate() == 1_000
    assert parser.parse(["ten", "thousand"]).evaluate() == 10_000
    assert parser.parse(["nine", "hundred", "thousand"]).evaluate() == 900_000
    
    # Test with additional hundreds/tens/ones
    assert parser.parse(["one", "thousand", "one"]).evaluate() == 1_001
    assert parser.parse(["one", "thousand", "one", "hundred"]).evaluate() == 1_100
    assert parser.parse(["one", "thousand", "one", "hundred", "one"]).evaluate() == 1_101


def test_millions_and_billions(parser):
    assert parser.parse(["one", "million"]).evaluate() == 1_000_000
    assert parser.parse(["one", "billion"]).evaluate() == 1_000_000_000
    
    # Test complex numbers
    assert parser.parse(["one", "million", "two", "hundred", "thousand"]).evaluate() == 1_200_000
    assert parser.parse(["one", "billion", "one", "million", "one"]).evaluate() == 1_001_000_001


def test_ordinal_numbers(parser):
    # Test basic ordinals
    assert parser.parse(["first"]).evaluate() == 1
    assert parser.parse(["second"]).evaluate() == 2
    assert parser.parse(["third"]).evaluate() == 3
    
    # Test compound ordinals
    assert parser.parse(["twenty", "first"]).evaluate() == 21
    assert parser.parse(["thirty", "second"]).evaluate() == 32
    
    # Test magnitude ordinals
    assert parser.parse(["hundredth"]).evaluate() == 100
    assert parser.parse(["one", "hundredth"]).evaluate() == 100
    assert parser.parse(["thousandth"]).evaluate() == 1_000
    assert parser.parse(["millionth"]).evaluate() == 1_000_000


def test_decimal_numbers(parser):
    # Test simple decimals
    assert parser.parse(["one", "point", "zero"]).evaluate() == 1.0
    assert parser.parse(["zero", "point", "five"]).evaluate() == 0.5
    assert parser.parse(["three", "point", "one", "four"]).evaluate() == 3.14
    
    # Test complex decimals
    assert parser.parse(["one", "hundred", "point", "zero", "one"]).evaluate() == 100.01
    assert parser.parse(["one", "thousand", "point", "one"]).evaluate() == 1000.1


def test_invalid_inputs(parser):
    with pytest.raises(ParsingError):
        parser.parse(["invalid"]).evaluate()
    
    with pytest.raises(ParsingError):
        parser.parse(["one", "invalid"]).evaluate()
    
    with pytest.raises(ParsingError):
        parser.parse(["fiveteen", "six"]).evaluate()  # Incorrect spelling


def test_edge_cases(parser):
    # Test empty input
    assert parser.parse([]).evaluate() == 0
    
    # Test with 'and'
    assert parser.parse(["one", "hundred", "and", "one"]).evaluate() == 101
    
    # Test hyphenated numbers
    assert parser.parse(["twenty-first"]).evaluate() == 21
    assert parser.parse(["ninety-ninth"]).evaluate() == 99 