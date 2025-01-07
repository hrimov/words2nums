from words2nums.locales.english.grammar_parser import GrammarParser
from words2nums.locales.english.tree import (
    DigitNode, MagnitudeNode, CompoundNode,
    DecimalNode, OrdinalNode
)


def test_make_trillions():
    parser = GrammarParser()
    t = DigitNode(1)
    b = DigitNode(2)
    
    result = parser._make_trillions(t, b)
    assert isinstance(result, CompoundNode)
    magnitude_node = result.parts[0]
    assert isinstance(magnitude_node, MagnitudeNode)
    assert magnitude_node.multiplier == 1_000_000_000_000
    assert result.parts[1] == b
    
    result = parser._make_trillions(t, None)
    assert isinstance(result, MagnitudeNode)
    assert result.multiplier == 1_000_000_000_000


def test_make_billions():
    parser = GrammarParser()
    b = DigitNode(1)
    m = DigitNode(2)
    
    result = parser._make_billions(b, m)
    assert isinstance(result, CompoundNode)
    magnitude_node = result.parts[0]
    assert isinstance(magnitude_node, MagnitudeNode)
    assert magnitude_node.multiplier == 1_000_000_000
    assert result.parts[1] == m
    
    result = parser._make_billions(b, None)
    assert isinstance(result, MagnitudeNode)
    assert result.multiplier == 1_000_000_000


def test_make_hundreds():
    parser = GrammarParser()
    h = 1  # Test with integer input
    t = DigitNode(20)
    
    result = parser._make_hundreds(h, t)
    assert isinstance(result, CompoundNode)
    magnitude_node = result.parts[0]
    assert isinstance(magnitude_node, MagnitudeNode)
    assert magnitude_node.multiplier == 100
    assert result.parts[1] == t
    
    # Test with NumberNode input
    h_node = DigitNode(1)
    result = parser._make_hundreds(h_node, None)
    assert isinstance(result, MagnitudeNode)
    assert result.multiplier == 100


def test_make_float():
    parser = GrammarParser()
    whole = DigitNode(1)
    fraction = [DigitNode(2), DigitNode(3)]
    
    result = parser._make_float(whole, fraction)
    assert isinstance(result, DecimalNode)
    assert result.whole == whole
    assert result.fraction == fraction


def test_extend_decimal():
    parser = GrammarParser()
    digit = DigitNode(1)
    more = [DigitNode(2), DigitNode(3)]
    
    result = parser._extend_decimal(digit, more)
    assert isinstance(result, list)
    assert len(result) == 3
    assert result[0] == digit
    assert result[1:] == more


def test_make_ordinal():
    parser = GrammarParser()
    number = DigitNode(1)
    
    result = parser._make_ordinal(number)
    assert isinstance(result, OrdinalNode)
    assert result.number == number
