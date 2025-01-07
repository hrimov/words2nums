import pytest
from words2nums.core.exceptions import ParsingError
from words2nums.locales.english.parser import EnglishParser
from words2nums.locales.english.tree import (
    NumberNode, DigitNode, MagnitudeNode, CompoundNode,
    OrdinalNode, DecimalNode
)


def test_parse_empty_tokens():
    parser = EnglishParser()
    result = parser.parse([])
    assert isinstance(result, DigitNode)
    assert result.evaluate() == 0


def test_parse_whitespace_tokens():
    parser = EnglishParser()
    with pytest.raises(ParsingError):
        parser.parse([" ", ""])


def test_parse_hyphenated_tokens():
    parser = EnglishParser()
    result = parser.parse(["twenty-first"])
    assert isinstance(result, OrdinalNode)
    assert result.evaluate() == 21


def test_parse_fraction():
    parser = EnglishParser()
    result = parser._parse_fraction(["one", "two", "three"])
    assert len(result) == 3
    assert all(isinstance(node, DigitNode) for node in result)
    assert [node.evaluate() for node in result] == [1, 2, 3]


def test_parse_with_grammar_invalid():
    parser = EnglishParser()
    with pytest.raises(ParsingError):
        parser._parse_with_grammar(["invalid", "tokens"])


def test_parse_with_grammar_hyphenated():
    parser = EnglishParser()
    result = parser._parse_with_grammar(["twenty-first"])
    assert isinstance(result, OrdinalNode)
    assert result.evaluate() == 21


def test_parse_with_grammar_magnitude():
    parser = EnglishParser()
    result = parser._parse_with_grammar(["one", "hundred"])
    assert isinstance(result, MagnitudeNode)
    assert result.evaluate() == 100


def test_parse_with_grammar_decimal():
    parser = EnglishParser()
    result = parser._parse_with_grammar(["one", "point", "two"])
    assert isinstance(result, DecimalNode)
    assert result.evaluate() == 1.2


def test_parse_with_grammar_ordinal():
    parser = EnglishParser()
    result = parser._parse_with_grammar(["first"])
    assert isinstance(result, OrdinalNode)
    assert result.evaluate() == 1


def test_parse_with_grammar_compound():
    parser = EnglishParser()
    result = parser._parse_with_grammar(["one", "hundred", "twenty", "three"])
    assert isinstance(result, CompoundNode)
    assert result.evaluate() == 123


def test_transformer_methods():
    parser = EnglishParser()
    transformer = parser.NumberTransformer(parser)
    
    # Test start method
    result = transformer.start([DigitNode(1)])
    assert isinstance(result, NumberNode)
    assert result.evaluate() == 1
    
    # Test number method
    result = transformer.number([DigitNode(2)])
    assert isinstance(result, NumberNode)
    assert result.evaluate() == 2
    
    # Test simple_number method
    result = transformer.simple_number(["one"])
    assert isinstance(result, NumberNode)
    assert result.evaluate() == 1
    
    # Test floating_point_number method
    result = transformer.floating_point_number([DigitNode(1), "point", DigitNode(2)])
    assert isinstance(result, DecimalNode)
    assert result.evaluate() == 1.2


def test_transformer_invalid_magnitude():
    parser = EnglishParser()
    transformer = parser.NumberTransformer(parser)
    
    with pytest.raises(ParsingError):
        transformer.magnitude_number([DigitNode(1), "invalid"])


def test_transformer_invalid_magnitude_format():
    parser = EnglishParser()
    transformer = parser.NumberTransformer(parser)
    
    with pytest.raises(ParsingError):
        transformer.magnitude_number([DigitNode(1), DigitNode(2), "hundred"])


def test_parse_with_grammar_no_lark():
    parser = EnglishParser()
    parser._grammar_parser = None
    with pytest.raises(NotImplementedError):
        parser._parse_with_grammar(["one"])


def test_parse_with_grammar_invalid_tree():
    parser = EnglishParser()
    with pytest.raises(ParsingError):
        parser._parse_with_grammar(["invalid"])


def test_parse_with_grammar_compound_with_magnitude():
    parser = EnglishParser()
    result = parser._parse_with_grammar(["one", "hundred", "and", "twenty", "three"])
    assert isinstance(result, CompoundNode)
    assert result.evaluate() == 123


def test_parse_with_grammar_multiple_magnitudes():
    parser = EnglishParser()
    result = parser._parse_with_grammar(["one", "million", "two", "hundred", "thousand"])
    assert isinstance(result, CompoundNode)
    assert result.evaluate() == 1_200_000


def test_parse_with_grammar_ordinal_with_magnitude():
    parser = EnglishParser()
    result = parser._parse_with_grammar(["one", "hundred", "and", "twenty", "third"])
    assert isinstance(result, OrdinalNode)
    assert result.evaluate() == 123


def test_parse_with_grammar_decimal_with_magnitude():
    parser = EnglishParser()
    result = parser._parse_with_grammar(["one", "hundred", "point", "two", "three"])
    assert isinstance(result, DecimalNode)
    assert result.evaluate() == 100.23 