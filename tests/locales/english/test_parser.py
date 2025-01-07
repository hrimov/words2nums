import pytest
from words2nums.locales.english.parser import EnglishParser
from words2nums.core.exceptions import ParsingError
from words2nums.locales.english.tree import (
    DigitNode, DecimalNode
)
from unittest.mock import Mock
from lark import Token
from unittest.mock import call


@pytest.fixture
def parser():
    """Fixture for testing actual parsing functionality"""
    return EnglishParser()


@pytest.fixture
def mock_parser():
    """Fixture for testing transformer and internal methods"""
    parser = EnglishParser()
    parser.convert_cardinal = Mock()
    parser.make_ordinal = Mock()
    parser.make_float = Mock()
    return parser


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


def test_parse_with_grammar_errors(mock_parser):
    # Test when grammar parser is not available
    mock_parser._grammar_parser = None
    with pytest.raises(NotImplementedError):
        mock_parser._parse_with_grammar(["one"])

    # Test invalid grammar parsing
    mock_parser._grammar_parser = object()  # Mock parser that will fail
    with pytest.raises(ParsingError):
        mock_parser._parse_with_grammar(["invalid"])


class MockToken(Token):
    """Mock token for testing that mimics Lark's Token interface"""
    
    @classmethod
    def new_token(cls, value: str) -> Token:
        """Factory method to create new tokens"""
        # Use Token's own constructor with minimal required arguments
        return Token('MOCK', value)


def test_transformer_methods(mock_parser):
    transformer = mock_parser.NumberTransformer(mock_parser)
    
    # Mock parser methods
    mock_parser.convert_cardinal = Mock(return_value=DigitNode(42))
    mock_parser.make_ordinal = Mock(return_value=DigitNode(42))
    mock_parser.make_float = Mock(return_value=DecimalNode(DigitNode(1), [DigitNode(2), DigitNode(3)]))
    
    # Test cardinal number
    tokens = [MockToken.new_token("forty"), MockToken.new_token("two")]
    result = transformer.simple_number(tokens)
    assert result.evaluate() == 42
    mock_parser.convert_cardinal.assert_called_once_with("forty two")
    
    # Test ordinal number
    mock_parser.convert_cardinal.reset_mock()
    tokens = [DigitNode(40), MockToken.new_token("second")]
    result = transformer.ordinal_number(tokens)
    assert result.evaluate() == 42
    mock_parser.make_ordinal.assert_called_once()
    
    # Test floating point number
    mock_parser.convert_cardinal.reset_mock()
    tokens = [DigitNode(1), MockToken.new_token("point"), DigitNode(23)]
    result = transformer.floating_point_number(tokens)
    assert result.evaluate() == 1.23
    mock_parser.make_float.assert_called_once()


def test_transformer_errors(mock_parser):
    transformer = mock_parser.NumberTransformer(mock_parser)
    
    # Mock all parser methods to raise errors
    error = ParsingError("Invalid number")
    mock_parser.convert_cardinal = Mock(side_effect=error)
    mock_parser.convert_ordinal = Mock(side_effect=error)
    mock_parser.make_ordinal = Mock(side_effect=error)
    mock_parser.make_float = Mock(side_effect=error)
    
    # Test invalid simple number
    with pytest.raises(ParsingError):
        transformer.simple_number([MockToken.new_token("invalid")])
    mock_parser.convert_cardinal.assert_called_once_with("invalid")
    
    # Test invalid magnitude number with two items
    mock_parser.convert_cardinal.reset_mock()
    with pytest.raises(ParsingError):
        transformer.magnitude_number([
            MockToken.new_token("one"),
            MockToken.new_token("hundred")
        ])
    # First converts the base number
    mock_parser.convert_cardinal.assert_called_once_with("one")
    
    # Test invalid magnitude number with three items
    mock_parser.convert_cardinal.reset_mock()
    with pytest.raises(ParsingError):
        transformer.magnitude_number([
            MockToken.new_token("one"),
            MockToken.new_token("hundred"),
            MockToken.new_token("two")
        ])
    # First converts the first number
    mock_parser.convert_cardinal.assert_called_once_with("one")
    
    # Test invalid ordinal number
    mock_parser.convert_cardinal.reset_mock()
    with pytest.raises(ParsingError):
        transformer.ordinal_number([MockToken.new_token("invalid")])
    mock_parser.convert_ordinal.assert_called_once_with("invalid")
    
    # Test invalid float number
    mock_parser.convert_cardinal.reset_mock()
    with pytest.raises(ParsingError):
        transformer.floating_point_number([
            MockToken.new_token("one"),
            MockToken.new_token("point"), 
            MockToken.new_token("two")
        ])
    # Should be called once for whole part
    mock_parser.convert_cardinal.assert_called_once_with("one")


def test_parse_large_ordinal_numbers(parser):
    """Test ordinal numbers with values >= 100"""
    # Test basic ordinal numbers
    assert parser.parse(["hundredth"]).evaluate() == 100
    assert parser.parse(["thousandth"]).evaluate() == 1000
    assert parser.parse(["millionth"]).evaluate() == 1000000
    
    # Test ordinal with base number
    assert parser.parse(["one", "hundredth"]).evaluate() == 100
    assert parser.parse(["two", "hundredth"]).evaluate() == 200
    assert parser.parse(["five", "thousandth"]).evaluate() == 5000
    
    # Test compound numbers ending in ordinal
    assert parser.parse(["one", "hundred", "first"]).evaluate() == 101
    assert parser.parse(["two", "hundred", "second"]).evaluate() == 202
    assert parser.parse(["five", "hundred", "third"]).evaluate() == 503
    
    # Test edge cases around 100
    assert parser.parse(["ninety", "ninth"]).evaluate() == 99  # < 100
    assert parser.parse(["hundredth"]).evaluate() == 100  # == 100
    assert parser.parse(["one", "hundred", "first"]).evaluate() == 101  # > 100
    
    # Test hyphenated ordinals
    assert parser.parse(["twenty-first"]).evaluate() == 21
    assert parser.parse(["ninety-ninth"]).evaluate() == 99


def test_grammar_parser_parsing(mock_parser, monkeypatch):
    """Test parsing using the generated grammar parser"""
    # Mock VALID_TOKENS to include our test tokens
    test_tokens = {"one", "two", "forty", "twenty-first"}
    monkeypatch.setattr('words2nums.locales.english.parser.VALID_TOKENS', test_tokens)
    
    # Mock successful parsing
    mock_tree = DigitNode(42)
    mock_parser._grammar_parser = Mock()
    mock_parser._grammar_parser.parse = Mock(return_value=mock_tree)
    
    # Test successful parsing with valid tokens
    result = mock_parser._parse_with_grammar(["forty", "two"])
    assert result == mock_tree
    mock_parser._grammar_parser.parse.assert_called_once_with("forty two")
    
    # Test invalid tokens
    with pytest.raises(ParsingError, match="No valid tokens found"):
        mock_parser._parse_with_grammar(["invalid", "tokens"])
    
    # Test parsing returns None with valid tokens
    mock_parser._grammar_parser.parse = Mock(return_value=None)
    with pytest.raises(ParsingError, match="Grammar parser returned invalid type"):
        mock_parser._parse_with_grammar(["one", "two"])
    
    # Test parsing raises exception with valid tokens
    mock_parser._grammar_parser.parse = Mock(side_effect=Exception("Parse error"))
    with pytest.raises(ParsingError, match="Grammar parsing failed: Parse error"):
        mock_parser._parse_with_grammar(["one", "two"])
    
    # Test hyphenated valid tokens
    mock_parser._grammar_parser.parse = Mock(return_value=mock_tree)
    result = mock_parser._parse_with_grammar(["twenty-first"])
    assert result == mock_tree
    mock_parser._grammar_parser.parse.assert_called_with("twenty-first")
