from words2nums.locales.english.grammar_parser import GrammarParser
from words2nums.locales.english.tokenizer import (
    WORD_TO_VALUE_MAP,
    ORDINAL_TO_CARDINAL_MAP
)
from words2nums.locales.english.tree import (
    DigitNode, MagnitudeNode, CompoundNode,
    DecimalNode, OrdinalNode, NumberNode, TensNode
)
from words2nums.core.exceptions import ParsingError
import pytest
from typing import Optional, Union, List, cast
from dataclasses import dataclass


@dataclass
class MockTrillions:
    t: str
    b: Optional[str] = None


@dataclass
class MockBillions:
    b: str
    m: Optional[str] = None


@dataclass
class MockMillions:
    m: str
    t: Optional[str] = None


@dataclass
class MockThousands:
    t: str
    h: Optional[str] = None


@dataclass
class MockHundreds:
    h: str
    t: Optional[str] = None


@dataclass
class MockTens:
    t: str
    o: Optional[str] = None


@dataclass
class MockOrdinal:
    value: str


@dataclass
class MockNode:
    trillions: Optional[MockTrillions] = None
    billions: Optional[MockBillions] = None
    millions: Optional[MockMillions] = None
    thousands: Optional[MockThousands] = None
    hundreds: Optional[MockHundreds] = None
    tens: Optional[MockTens] = None
    ordinal: Optional[MockOrdinal] = None
    
    def split(self) -> List['MockNode']:
        """Mock split method to prevent string splitting"""
        return [self]


def test_convert_trillions():
    """Test converting trillion numbers"""
    parser = GrammarParser()
    
    # Mock tree_builder to handle our mock nodes
    def mock_convert(node: Union[MockNode, str]) -> NumberNode:
        if isinstance(node, MockNode) and node.trillions is not None:
            t = DigitNode(WORD_TO_VALUE_MAP[node.trillions.t])
            b: Optional[NumberNode] = None
            if node.trillions.b is not None:
                # Create a MagnitudeNode for billions
                b_value = DigitNode(WORD_TO_VALUE_MAP[node.trillions.b])
                b = MagnitudeNode(base=b_value, multiplier=1_000_000_000)
            return parser._make_trillions(t, b)
        elif isinstance(node, str):
            return DigitNode(WORD_TO_VALUE_MAP[node])
        else:
            raise ParsingError("Invalid node type")
    
    parser._convert_cardinal = mock_convert
    
    # Test simple trillion
    node = MockNode(trillions=MockTrillions(t="one"))
    result = parser._convert_cardinal(node)
    assert result.evaluate() == 1_000_000_000_000
    
    # Test trillion with billions
    node = MockNode(trillions=MockTrillions(t="one", b="two"))
    result = parser._convert_cardinal(node)
    assert result.evaluate() == 1_000_000_000_000 + 2_000_000_000
    
    # Test multiple trillions
    node = MockNode(trillions=MockTrillions(t="five"))
    result = parser._convert_cardinal(node)
    assert result.evaluate() == 5_000_000_000_000
    
    # Test complex trillion number
    node = MockNode(trillions=MockTrillions(t="twenty", b="five"))
    result = parser._convert_cardinal(node)
    assert result.evaluate() == 20_000_000_000_000 + 5_000_000_000


def test_make_trillions():
    parser = GrammarParser()
    base = DigitNode(1)
    result = parser._make_trillions(base, None)
    assert isinstance(result, MagnitudeNode)
    assert result.evaluate() == 1_000_000_000_000
    
    # Test with billions
    base = DigitNode(1)
    bil_base = DigitNode(2)
    bil = MagnitudeNode(base=bil_base, multiplier=1_000_000_000)
    result = parser._make_trillions(base, bil)
    assert isinstance(result, CompoundNode)
    assert result.evaluate() == 1_000_000_000_000 + 2_000_000_000


def test_make_billions():
    parser = GrammarParser()
    base = DigitNode(1)
    result = parser._make_billions(base, None)
    assert isinstance(result, MagnitudeNode)
    assert result.evaluate() == 1_000_000_000
    
    # Test with millions
    base = DigitNode(1)
    mil_base = DigitNode(2)
    mil = MagnitudeNode(base=mil_base, multiplier=1_000_000)
    result = parser._make_billions(base, mil)
    assert isinstance(result, CompoundNode)
    assert result.evaluate() == 1_000_000_000 + 2_000_000


def test_make_millions():
    parser = GrammarParser()
    base = DigitNode(1)
    result = parser._make_millions(base, None)
    assert isinstance(result, MagnitudeNode)
    assert result.evaluate() == 1_000_000
    
    # Test with thousands
    base = DigitNode(1)
    thou_base = DigitNode(2)
    thou = MagnitudeNode(base=thou_base, multiplier=1_000)
    result = parser._make_millions(base, thou)
    assert isinstance(result, CompoundNode)
    assert result.evaluate() == 1_000_000 + 2_000


def test_make_thousands():
    parser = GrammarParser()
    base = DigitNode(1)
    result = parser._make_thousands(base, None)
    assert isinstance(result, MagnitudeNode)
    assert result.evaluate() == 1_000
    
    # Test with hundreds
    base = DigitNode(1)
    hund_base = DigitNode(2)
    hund = MagnitudeNode(base=hund_base, multiplier=100)
    result = parser._make_thousands(base, hund)
    assert isinstance(result, CompoundNode)
    assert result.evaluate() == 1_000 + 200


def test_make_hundreds():
    parser = GrammarParser()
    base = DigitNode(1)
    result = parser._make_hundreds(base, None)
    assert isinstance(result, MagnitudeNode)
    assert result.evaluate() == 100
    
    # Test with tens
    base = DigitNode(1)
    tens = DigitNode(20)
    result = parser._make_hundreds(base, tens)
    assert isinstance(result, CompoundNode)
    assert result.evaluate() == 100 + 20


def test_make_tens():
    parser = GrammarParser()
    base = DigitNode(20)
    result = parser._make_tens(base, None)
    assert isinstance(result, NumberNode)
    assert result.evaluate() == 20
    
    # Test with ones
    base = DigitNode(20)
    ones = DigitNode(1)
    result = parser._make_tens(base, ones)
    assert isinstance(result, CompoundNode)
    assert result.evaluate() == 21


def test_make_ordinal():
    parser = GrammarParser()
    number = DigitNode(1)
    
    result = parser._make_ordinal(number)
    assert isinstance(result, OrdinalNode)
    assert result.number == number


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


def test_convert_cardinal_all_magnitudes():
    """Test converting numbers of all magnitudes"""
    parser = GrammarParser()
    
    def mock_convert(node: Union[MockNode, str]) -> NumberNode:
        if isinstance(node, str):
            if node in WORD_TO_VALUE_MAP:
                return DigitNode(WORD_TO_VALUE_MAP[node])
            elif node in ORDINAL_TO_CARDINAL_MAP:
                return OrdinalNode(DigitNode(ORDINAL_TO_CARDINAL_MAP[node]))
            raise ParsingError(f"Unknown word: {node}")
        
        if node.trillions is not None:
            t = cast(NumberNode, mock_convert(node.trillions.t))
            b: Optional[NumberNode] = None
            if node.trillions.b is not None:
                b = cast(NumberNode, mock_convert(node.trillions.b))
            return parser._make_trillions(t, b)
        
        if node.billions is not None:
            b = cast(NumberNode, mock_convert(node.billions.b))
            m: Optional[NumberNode] = None
            if node.billions.m is not None:
                m = cast(NumberNode, mock_convert(node.billions.m))
            return parser._make_billions(b, m)
        
        if node.millions is not None:
            m = cast(NumberNode, mock_convert(node.millions.m))
            thou: Optional[NumberNode] = None
            if node.millions.t is not None:
                thou = cast(NumberNode, mock_convert(node.millions.t))
            return parser._make_millions(m, thou)
        
        if node.thousands is not None:
            thou = cast(NumberNode, mock_convert(node.thousands.t))
            h: Optional[NumberNode] = None
            if node.thousands.h is not None:
                h = cast(NumberNode, mock_convert(node.thousands.h))
            return parser._make_thousands(thou, h)
        
        if node.hundreds is not None:
            h = cast(NumberNode, mock_convert(node.hundreds.h))
            tens: Optional[NumberNode] = None
            if node.hundreds.t is not None:
                tens = cast(NumberNode, mock_convert(node.hundreds.t))
            return parser._make_hundreds(h, tens)
        
        if node.tens is not None:
            tens = cast(NumberNode, mock_convert(node.tens.t))
            ones: Optional[NumberNode] = None
            if node.tens.o is not None:
                ones = cast(NumberNode, mock_convert(node.tens.o))
            return parser._make_tens(tens, ones)
        
        if node.ordinal is not None:
            return OrdinalNode(DigitNode(ORDINAL_TO_CARDINAL_MAP[node.ordinal.value]))
        
        raise ParsingError("Invalid node type")
    
    parser._convert_cardinal = mock_convert
    
    # Test all magnitudes
    node = MockNode(trillions=MockTrillions(t="one"))
    result = parser._convert_cardinal(node)
    assert result.evaluate() == 1_000_000_000_000
    
    node = MockNode(billions=MockBillions(b="one"))
    result = parser._convert_cardinal(node)
    assert result.evaluate() == 1_000_000_000
    
    node = MockNode(millions=MockMillions(m="one"))
    result = parser._convert_cardinal(node)
    assert result.evaluate() == 1_000_000
    
    node = MockNode(thousands=MockThousands(t="one"))
    result = parser._convert_cardinal(node)
    assert result.evaluate() == 1_000
    
    node = MockNode(hundreds=MockHundreds(h="one"))
    result = parser._convert_cardinal(node)
    assert result.evaluate() == 100
    
    node = MockNode(tens=MockTens(t="twenty"))
    result = parser._convert_cardinal(node)
    assert result.evaluate() == 20
    
    node = MockNode(ordinal=MockOrdinal(value="first"))
    result = parser._convert_cardinal(node)
    assert result.evaluate() == 1


def test_convert_cardinal_string_input():
    """Test convert_cardinal with string input"""
    parser = GrammarParser()
    
    # Test empty string
    with pytest.raises(ParsingError, match="Empty string is not a valid number"):
        parser.convert_cardinal("")
    
    # Test single valid word
    result = parser.convert_cardinal("one")
    assert isinstance(result, DigitNode)
    assert result.evaluate() == 1
    
    # Test single ordinal word
    result = parser.convert_cardinal("first")
    assert isinstance(result, OrdinalNode)
    assert result.evaluate() == 1
    
    # Test multiple valid words
    result = parser.convert_cardinal("twenty one")
    assert result.evaluate() == 21
    
    # Test with punctuation
    result = parser.convert_cardinal("one hundred and twenty")
    assert result.evaluate() == 120
    
    # Test with invalid tokens
    with pytest.raises(ParsingError, match="Invalid tokens found:"):
        parser.convert_cardinal("one two invalid")
    
    # Test with only punctuation
    with pytest.raises(ParsingError, match="No valid tokens found"):
        parser.convert_cardinal("and")


def test_convert_ordinal():
    """Test convert_ordinal method"""
    parser = GrammarParser()
    
    # Test simple ordinals
    result = parser.convert_ordinal("first")
    assert isinstance(result, OrdinalNode)
    assert result.evaluate() == 1
    
    result = parser.convert_ordinal("second")
    assert isinstance(result, OrdinalNode)
    assert result.evaluate() == 2
    
    result = parser.convert_ordinal("third")
    assert isinstance(result, OrdinalNode)
    assert result.evaluate() == 3
    
    # Test ordinals with magnitude
    result = parser.convert_ordinal("hundredth")
    assert isinstance(result, OrdinalNode)
    assert result.evaluate() == 100
    
    result = parser.convert_ordinal("thousandth")
    assert isinstance(result, OrdinalNode)
    assert result.evaluate() == 1000
    
    result = parser.convert_ordinal("millionth")
    assert isinstance(result, OrdinalNode)
    assert result.evaluate() == 1000000
    
    # Test invalid input
    with pytest.raises(ParsingError):
        parser.convert_ordinal("invalid")
    
    with pytest.raises(ParsingError):
        parser.convert_ordinal("one")  # Cardinal number should fail
    
    with pytest.raises(ParsingError):
        parser.convert_ordinal("")


def test_convert_cardinal_error_handling():
    """Test error handling in convert_cardinal"""
    parser = GrammarParser()
    
    # Test unknown word
    with pytest.raises(ParsingError, match="Invalid tokens found:"):
        parser.convert_cardinal("unknown")
    
    # Test unknown node type
    class UnknownNode:
        pass
    
    with pytest.raises(ParsingError, match="Unknown node type:"):
        parser._convert_cardinal(UnknownNode())


def test_make_ordinal_error_handling():
    """Test error handling in make_ordinal"""
    parser = GrammarParser()
    with pytest.raises(ParsingError):
        parser._make_ordinal("invalid")


def test_make_float_error_handling():
    """Test error handling in make_float"""
    parser = GrammarParser()
    
    # Test with empty fraction list
    whole = DigitNode(1)
    result = parser.make_float(whole, [])
    assert isinstance(result, DecimalNode)
    assert result.evaluate() == 1.0
    
    # Test with multiple fraction digits
    whole = DigitNode(1)
    fraction = [DigitNode(2), DigitNode(3), DigitNode(4)]
    result = parser.make_float(whole, fraction)
    assert isinstance(result, DecimalNode)
    assert result.evaluate() == 1.234


def test_extend_decimal_error_handling():
    """Test error handling in extend_decimal"""
    parser = GrammarParser()
    
    # Test with empty more list
    digit = DigitNode(1)
    result = parser._extend_decimal(digit, [])
    assert len(result) == 1
    assert result[0].evaluate() == 1
    
    # Test with multiple digits
    digit = DigitNode(1)
    more = [DigitNode(2), DigitNode(3)]
    result = parser._extend_decimal(digit, more)
    assert len(result) == 3
    assert [d.evaluate() for d in result] == [1, 2, 3]


def test_convert_cardinal_complex_nodes():
    """Test convert_cardinal with complex node structures"""
    parser = GrammarParser()
    
    # Test nested nodes
    class MockBillions:
        b = "one"
        m = None
    
    class ComplexNode:
        billions = MockBillions()
        trillions = None
        millions = None
        thousands = None
        hundreds = None
        tens = None
        ordinal = None
    
    result = parser._convert_cardinal(ComplexNode())
    assert result.evaluate() == 1_000_000_000
    
    # Test with all attributes set to None
    class EmptyNode:
        trillions = None
        billions = None
        millions = None
        thousands = None
        hundreds = None
        tens = None
        ordinal = None
    
    with pytest.raises(ParsingError, match="Unknown node type:"):
        parser._convert_cardinal(EmptyNode())
    
    # Test with invalid node type
    class InvalidNode:
        pass
    
    with pytest.raises(ParsingError, match="Unknown node type:"):
        parser._convert_cardinal(InvalidNode())
    
    # Test with complex nested structure
    class MockTens:
        def __init__(self):
            self.t = "twenty"
            self.o = "one"
            self.trillions = None
            self.billions = None
            self.millions = None
            self.thousands = None
            self.hundreds = None
            self.tens = None
            self.ordinal = None

    class MockHundreds:
        def __init__(self):
            self.h = "one"
            self.t = MockTens()
            self.trillions = None
            self.billions = None
            self.millions = None
            self.thousands = None
            self.hundreds = None
            self.tens = None
            self.ordinal = None

    class ComplexNestedNode:
        def __init__(self):
            self.hundreds = MockHundreds()
            self.trillions = None
            self.billions = None
            self.millions = None
            self.thousands = None
            self.tens = None
            self.ordinal = None

    result = parser._convert_cardinal(ComplexNestedNode())
    assert result.evaluate() == 121


def test_convert_cardinal_all_word_values():
    """Test convert_cardinal with all possible word values"""
    parser = GrammarParser()
    
    # Test all cardinal numbers
    for word, value in WORD_TO_VALUE_MAP.items():
        result = parser.convert_cardinal(word)
        assert result.evaluate() == value
    
    # Test all ordinal numbers
    for word, value in ORDINAL_TO_CARDINAL_MAP.items():
        result = parser.convert_cardinal(word)
        assert result.evaluate() == value


def test_convert_cardinal_node_types():
    """Test convert_cardinal with different node types"""
    parser = GrammarParser()
    
    # Test with trillions node
    node = MockNode(trillions=MockTrillions(t="one"))
    result = parser._convert_cardinal(node)
    assert isinstance(result, MagnitudeNode)
    assert result.evaluate() == 1_000_000_000_000
    
    # Test with billions node
    node = MockNode(billions=MockBillions(b="one"))
    result = parser._convert_cardinal(node)
    assert isinstance(result, MagnitudeNode)
    assert result.evaluate() == 1_000_000_000
    
    # Test with millions node
    node = MockNode(millions=MockMillions(m="one"))
    result = parser._convert_cardinal(node)
    assert isinstance(result, MagnitudeNode)
    assert result.evaluate() == 1_000_000
    
    # Test with thousands node
    node = MockNode(thousands=MockThousands(t="one"))
    result = parser._convert_cardinal(node)
    assert isinstance(result, MagnitudeNode)
    assert result.evaluate() == 1_000
    
    # Test with hundreds node
    node = MockNode(hundreds=MockHundreds(h="one"))
    result = parser._convert_cardinal(node)
    assert isinstance(result, MagnitudeNode)
    assert result.evaluate() == 100
    
    # Test with tens node
    node = MockNode(tens=MockTens(t="twenty"))
    result = parser._convert_cardinal(node)
    assert isinstance(result, DigitNode)
    assert result.evaluate() == 20


def test_convert_cardinal_compound_nodes():
    """Test convert_cardinal with compound nodes"""
    parser = GrammarParser()
    
    # Test trillions with billions
    node = MockNode(trillions=MockTrillions(t="one", b="two"))
    result = parser._convert_cardinal(node)
    assert isinstance(result, CompoundNode)
    assert result.evaluate() == 1_000_000_000_000 + 2_000_000_000
    
    # Test billions with millions
    node = MockNode(billions=MockBillions(b="one", m="two"))
    result = parser._convert_cardinal(node)
    assert isinstance(result, CompoundNode)
    assert result.evaluate() == 1_000_000_000 + 2_000_000
    
    # Test millions with thousands
    node = MockNode(millions=MockMillions(m="one", t="two"))
    result = parser._convert_cardinal(node)
    assert isinstance(result, CompoundNode)
    assert result.evaluate() == 1_000_000 + 2_000
    
    # Test thousands with hundreds
    node = MockNode(thousands=MockThousands(t="one", h="two"))
    result = parser._convert_cardinal(node)
    assert isinstance(result, CompoundNode)
    assert result.evaluate() == 1_000 + 200
    
    # Test hundreds with tens
    node = MockNode(hundreds=MockHundreds(h="one", t="twenty"))
    result = parser._convert_cardinal(node)
    assert isinstance(result, CompoundNode)
    assert result.evaluate() == 100 + 20
    
    # Test tens with ones
    node = MockNode(tens=MockTens(t="twenty", o="one"))
    result = parser._convert_cardinal(node)
    assert isinstance(result, CompoundNode)
    assert result.evaluate() == 21


def test_convert_cardinal_edge_cases():
    """Test convert_cardinal with edge cases"""
    parser = GrammarParser()
    
    # Test empty string
    with pytest.raises(ParsingError):
        parser.convert_cardinal("")
    
    # Test None
    with pytest.raises(ParsingError):
        parser.convert_cardinal(None)
    
    # Test invalid string
    with pytest.raises(ParsingError):
        parser.convert_cardinal("invalid")
    
    # Test invalid node type
    class InvalidNode:
        pass
    
    with pytest.raises(ParsingError):
        parser._convert_cardinal(InvalidNode())


def test_convert_cardinal_node_attributes():
    """Test convert_cardinal with different node attributes"""
    parser = GrammarParser()
    
    # Test node with no recognized attributes
    class EmptyNode:
        pass
    
    with pytest.raises(ParsingError):
        parser._convert_cardinal(EmptyNode())
    
    # Test partial nodes
    class PartialTrillionsNode:
        class Trillions:
            t = "one"
        trillions = Trillions()
    
    result = parser._convert_cardinal(PartialTrillionsNode())
    assert result.evaluate() == 1_000_000_000_000
    
    class PartialBillionsNode:
        class Billions:
            b = "one"
        billions = Billions()
    
    result = parser._convert_cardinal(PartialBillionsNode())
    assert result.evaluate() == 1_000_000_000
    
    class PartialMillionsNode:
        class Millions:
            m = "one"
        millions = Millions()
    
    result = parser._convert_cardinal(PartialMillionsNode())
    assert result.evaluate() == 1_000_000
    
    class PartialThousandsNode:
        class Thousands:
            t = "one"
        thousands = Thousands()
    
    result = parser._convert_cardinal(PartialThousandsNode())
    assert result.evaluate() == 1_000
    
    class PartialHundredsNode:
        class Hundreds:
            h = "one"
        hundreds = Hundreds()
    
    result = parser._convert_cardinal(PartialHundredsNode())
    assert result.evaluate() == 100
    
    class PartialTensNode:
        class Tens:
            t = "twenty"
        tens = Tens()
    
    result = parser._convert_cardinal(PartialTensNode())
    assert result.evaluate() == 20


def test_convert_trillions():
    parser = GrammarParser()
    result = parser.convert_cardinal("one trillion")
    assert isinstance(result, MagnitudeNode)
    assert result.evaluate() == 1_000_000_000_000


def test_make_trillions():
    parser = GrammarParser()
    base = DigitNode(1)
    result = parser._make_trillions(base, None)
    assert isinstance(result, MagnitudeNode)
    assert result.evaluate() == 1_000_000_000_000
    
    # Test with billions
    base = DigitNode(1)
    bil_base = DigitNode(2)
    bil = MagnitudeNode(base=bil_base, multiplier=1_000_000_000)
    result = parser._make_trillions(base, bil)
    assert isinstance(result, CompoundNode)
    assert result.evaluate() == 1_000_000_000_000 + 2_000_000_000


def test_make_billions():
    parser = GrammarParser()
    base = DigitNode(1)
    result = parser._make_billions(base, None)
    assert isinstance(result, MagnitudeNode)
    assert result.evaluate() == 1_000_000_000
    
    # Test with millions
    base = DigitNode(1)
    mil_base = DigitNode(2)
    mil = MagnitudeNode(base=mil_base, multiplier=1_000_000)
    result = parser._make_billions(base, mil)
    assert isinstance(result, CompoundNode)
    assert result.evaluate() == 1_000_000_000 + 2_000_000


def test_make_millions():
    parser = GrammarParser()
    base = DigitNode(1)
    result = parser._make_millions(base, None)
    assert isinstance(result, MagnitudeNode)
    assert result.evaluate() == 1_000_000
    
    # Test with thousands
    base = DigitNode(1)
    thou_base = DigitNode(2)
    thou = MagnitudeNode(base=thou_base, multiplier=1_000)
    result = parser._make_millions(base, thou)
    assert isinstance(result, CompoundNode)
    assert result.evaluate() == 1_000_000 + 2_000


def test_make_thousands():
    parser = GrammarParser()
    base = DigitNode(1)
    result = parser._make_thousands(base, None)
    assert isinstance(result, MagnitudeNode)
    assert result.evaluate() == 1_000
    
    # Test with hundreds
    base = DigitNode(1)
    hund_base = DigitNode(2)
    hund = MagnitudeNode(base=hund_base, multiplier=100)
    result = parser._make_thousands(base, hund)
    assert isinstance(result, CompoundNode)
    assert result.evaluate() == 1_000 + 200


def test_make_hundreds():
    parser = GrammarParser()
    base = DigitNode(1)
    result = parser._make_hundreds(base, None)
    assert isinstance(result, MagnitudeNode)
    assert result.evaluate() == 100
    
    # Test with tens
    base = DigitNode(1)
    tens = DigitNode(20)
    result = parser._make_hundreds(base, tens)
    assert isinstance(result, CompoundNode)
    assert result.evaluate() == 100 + 20


def test_make_tens():
    parser = GrammarParser()
    base = DigitNode(20)
    result = parser._make_tens(base, None)
    assert isinstance(result, NumberNode)
    assert result.evaluate() == 20
    
    # Test with ones
    base = DigitNode(20)
    ones = DigitNode(1)
    result = parser._make_tens(base, ones)
    assert isinstance(result, CompoundNode)
    assert result.evaluate() == 21


def test_make_ordinal():
    parser = GrammarParser()
    number = DigitNode(1)
    result = parser.make_ordinal(number)
    assert isinstance(result, OrdinalNode)
    assert result.evaluate() == 1


def test_make_float():
    parser = GrammarParser()
    whole = DigitNode(1)
    fraction = [DigitNode(2), DigitNode(3)]
    result = parser.make_float(whole, fraction)
    assert isinstance(result, DecimalNode)
    assert result.evaluate() == 1.23


def test_extend_decimal():
    parser = GrammarParser()
    digit = DigitNode(1)
    more = [DigitNode(2), DigitNode(3)]
    result = parser._extend_decimal(digit, more)
    assert isinstance(result, list)
    assert len(result) == 3
    assert result[0] == digit
    assert result[1:] == more


def test_convert_cardinal_all_magnitudes():
    parser = GrammarParser()
    numbers = [
        ("one trillion", 1_000_000_000_000),
        ("one billion", 1_000_000_000),
        ("one million", 1_000_000),
        ("one thousand", 1_000),
        ("one hundred", 100),
    ]
    for text, expected in numbers:
        result = parser.convert_cardinal(text)
        assert isinstance(result, MagnitudeNode)
        assert result.evaluate() == expected


def test_convert_cardinal_string_input():
    parser = GrammarParser()
    result = parser.convert_cardinal("twenty")
    assert isinstance(result, TensNode)
    assert result.evaluate() == 20


def test_convert_ordinal():
    parser = GrammarParser()
    result = parser.convert_ordinal("first")
    assert isinstance(result, OrdinalNode)
    assert result.evaluate() == 1


def test_convert_cardinal_error_handling():
    parser = GrammarParser()
    with pytest.raises(ParsingError):
        parser.convert_cardinal("invalid")


def test_make_ordinal_error_handling():
    parser = GrammarParser()
    with pytest.raises(ParsingError):
        parser._make_ordinal("invalid")


def test_make_float_error_handling():
    parser = GrammarParser()
    with pytest.raises(ParsingError):
        parser.make_float("invalid", [])


def test_extend_decimal_error_handling():
    parser = GrammarParser()
    with pytest.raises(ParsingError):
        parser.extend_decimal("invalid", DigitNode(1))


def test_convert_cardinal_complex_nodes():
    parser = GrammarParser()
    result = parser.convert_cardinal("one hundred twenty three")
    assert isinstance(result, CompoundNode)
    assert result.evaluate() == 123


def test_convert_cardinal_all_word_values():
    parser = GrammarParser()
    for word, value in {
        "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
        "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
        "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
        "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17,
        "eighteen": 18, "nineteen": 19, "twenty": 20,
    }.items():
        result = parser.convert_cardinal(word)
        assert result.evaluate() == value


def test_convert_cardinal_node_types():
    parser = GrammarParser()
    assert isinstance(parser.convert_cardinal("one"), DigitNode)
    assert isinstance(parser.convert_cardinal("twenty"), TensNode)
    assert isinstance(parser.convert_cardinal("one hundred"), MagnitudeNode)
    assert isinstance(parser.convert_cardinal("twenty one"), CompoundNode)


def test_convert_cardinal_compound_nodes():
    parser = GrammarParser()
    result = parser.convert_cardinal("twenty one")
    assert isinstance(result, CompoundNode)
    assert len(result.parts) == 2
    assert isinstance(result.parts[0], TensNode)
    assert isinstance(result.parts[1], DigitNode)
    assert result.evaluate() == 21


def test_convert_cardinal_edge_cases():
    parser = GrammarParser()
    assert parser.convert_cardinal("zero").evaluate() == 0
    assert parser.convert_cardinal("one").evaluate() == 1
    assert parser.convert_cardinal("twenty").evaluate() == 20
    assert parser.convert_cardinal("one hundred").evaluate() == 100


def test_convert_cardinal_node_attributes():
    parser = GrammarParser()
    digit = parser.convert_cardinal("one")
    assert hasattr(digit, "value")
    assert digit.value == 1

    tens = parser.convert_cardinal("twenty")
    assert hasattr(tens, "value")
    assert tens.value == 20

    magnitude = parser.convert_cardinal("one hundred")
    assert hasattr(magnitude, "base")
    assert hasattr(magnitude, "multiplier")
    assert magnitude.base.evaluate() == 1
    assert magnitude.multiplier == 100


def test_convert_cardinal_with_and():
    parser = GrammarParser()
    result = parser.convert_cardinal("one hundred and twenty three")
    assert isinstance(result, CompoundNode)
    assert result.evaluate() == 123


def test_convert_cardinal_with_multiple_magnitudes():
    parser = GrammarParser()
    result = parser.convert_cardinal("one million two hundred thousand")
    assert isinstance(result, CompoundNode)
    assert result.evaluate() == 1_200_000


def test_convert_cardinal_with_ordinal():
    parser = GrammarParser()
    result = parser.convert_cardinal("twenty first")
    assert isinstance(result, CompoundNode)
    assert result.evaluate() == 21


def test_convert_cardinal_with_decimal():
    parser = GrammarParser()
    result = parser.convert_cardinal("one point two three")
    assert isinstance(result, DecimalNode)
    assert result.evaluate() == 1.23


def test_convert_number_to_word():
    """Test converting numbers back to words"""
    parser = GrammarParser()
    
    # Test valid conversions
    assert parser._convert_number_to_word(1) == "one"
    assert parser._convert_number_to_word(20) == "twenty"
    assert parser._convert_number_to_word(90) == "ninety"
    
    # Test invalid conversion
    with pytest.raises(ParsingError):
        parser._convert_number_to_word(999999)  # Number not in WORD_TO_VALUE_MAP


def test_convert_cardinal_with_numeric_tokens():
    """Test converting strings containing numeric tokens"""
    parser = GrammarParser()
    
    # Test with invalid numeric tokens
    with pytest.raises(ParsingError):
        parser.convert_cardinal("1")
    
    with pytest.raises(ParsingError):
        parser.convert_cardinal("21")
    
    with pytest.raises(ParsingError):
        parser.convert_cardinal("1 hundred")
    
    with pytest.raises(ParsingError):
        parser.convert_cardinal("20 1")


def test_convert_cardinal_with_punctuation():
    """Test converting strings with punctuation"""
    parser = GrammarParser()
    
    # Test with invalid punctuation
    with pytest.raises(ParsingError):
        parser.convert_cardinal("one,")
    
    with pytest.raises(ParsingError):
        parser.convert_cardinal("twenty, one")
    
    with pytest.raises(ParsingError):
        parser.convert_cardinal("one hundred.")


def test_convert_cardinal_empty_input():
    """Test converting empty strings"""
    parser = GrammarParser()
    
    # Test empty string
    with pytest.raises(ParsingError):
        parser.convert_cardinal("")
    
    # Test string with only punctuation
    with pytest.raises(ParsingError):
        parser.convert_cardinal(",.")
    
    # Test string with only spaces
    with pytest.raises(ParsingError):
        parser.convert_cardinal("   ")


def test_convert_cardinal_invalid_tokens():
    """Test converting strings with invalid tokens"""
    parser = GrammarParser()
    
    # Test with invalid words
    with pytest.raises(ParsingError):
        parser.convert_cardinal("invalid")
    
    # Test with mixed valid and invalid tokens
    with pytest.raises(ParsingError):
        parser.convert_cardinal("one invalid")
    
    # Test with invalid numeric tokens
    with pytest.raises(ParsingError):
        parser.convert_cardinal("1.5")  # Decimal numbers not supported as tokens


def test_convert_cardinal_with_ordinal_tokens():
    """Test converting strings with ordinal tokens"""
    parser = GrammarParser()
    
    # Test single ordinal token
    assert parser.convert_cardinal("first").evaluate() == 1
    
    # Test ordinal token in compound number
    assert parser.convert_cardinal("twenty first").evaluate() == 21
    
    # Test ordinal token with magnitude
    assert parser.convert_cardinal("one hundredth").evaluate() == 101


def test_convert_cardinal_with_magnitude_tokens():
    """Test converting strings with magnitude tokens"""
    parser = GrammarParser()
    
    # Test various magnitude combinations
    assert parser.convert_cardinal("one thousand").evaluate() == 1000
    assert parser.convert_cardinal("one million").evaluate() == 1000000
    assert parser.convert_cardinal("one billion").evaluate() == 1000000000
    assert parser.convert_cardinal("one trillion").evaluate() == 1000000000000


def test_convert_cardinal_complex_combinations():
    """Test converting complex number combinations"""
    parser = GrammarParser()
    
    # Test complex combinations
    assert parser.convert_cardinal("one hundred twenty three million four hundred fifty six thousand seven hundred eighty nine").evaluate() == 123456789
    assert parser.convert_cardinal("nine hundred ninety nine trillion nine hundred ninety nine billion nine hundred ninety nine million nine hundred ninety nine thousand nine hundred ninety nine").evaluate() == 999999999999999


def test_convert_cardinal_with_invalid_node_types():
    """Test converting cardinal numbers with invalid node types"""
    parser = GrammarParser()
    
    class InvalidNode:
        def __init__(self):
            self.trillions = None
            self.billions = None
            self.millions = None
            self.thousands = None
            self.hundreds = None
            self.tens = None
            self.ordinal = "invalid"  # Invalid type for ordinal
    
    with pytest.raises(ParsingError):
        parser._convert_cardinal(InvalidNode())


def test_convert_cardinal_with_partial_nodes():
    """Test converting cardinal numbers with partially filled nodes"""
    parser = GrammarParser()
    
    class TensNode:
        def __init__(self):
            self.t = "twenty"
            self.o = None
    
    class PartialNode:
        def __init__(self):
            self.trillions = None
            self.billions = None
            self.millions = None
            self.thousands = None
            self.hundreds = None
            self.tens = TensNode()  # Only tens is set
            self.ordinal = None
    
    result = parser._convert_cardinal(PartialNode())
    assert result.evaluate() == 20


def test_convert_cardinal_with_invalid_attributes():
    """Test converting cardinal numbers with invalid node attributes"""
    parser = GrammarParser()
    
    class InvalidAttributeNode:
        def __init__(self):
            self.trillions = None
            self.billions = None
            self.millions = None
            self.thousands = None
            self.hundreds = None
            self.tens = type('obj', (), {'t': 'invalid', 'o': None})()  # Invalid value for tens
            self.ordinal = None
    
    with pytest.raises(ParsingError):
        parser._convert_cardinal(InvalidAttributeNode())


def test_convert_cardinal_with_mixed_types():
    """Test converting cardinal numbers with mixed node types"""
    parser = GrammarParser()
    
    class MixedTypeNode:
        def __init__(self):
            self.trillions = None
            self.billions = None
            self.millions = None
            self.thousands = None
            self.hundreds = type('obj', (), {'h': 'one', 't': 1})()
            self.tens = None
            self.ordinal = None
    
    with pytest.raises(ParsingError):
        parser._convert_cardinal(MixedTypeNode())


def test_convert_cardinal_with_invalid_tree_structure():
    """Test converting with invalid tree structure"""
    parser = GrammarParser()
    
    class InvalidTreeNode:
        def __init__(self):
            self.trillions = type('obj', (), {'t': 'invalid', 'b': None})()  # Invalid value for trillions
            self.billions = None
            self.millions = None
            self.thousands = None
            self.hundreds = None
            self.tens = None
            self.ordinal = None
    
    with pytest.raises(ParsingError):
        parser._convert_cardinal(InvalidTreeNode())


def test_convert_cardinal_with_invalid_node_values():
    """Test converting with invalid node values"""
    parser = GrammarParser()
    
    class InvalidValueNode:
        def __init__(self):
            self.trillions = type('obj', (), {'t': 123, 'b': None})()
            self.billions = None
            self.millions = None
            self.thousands = None
            self.hundreds = None
            self.tens = None
            self.ordinal = None
    
    with pytest.raises(ParsingError):
        parser._convert_cardinal(InvalidValueNode())


def test_convert_cardinal_with_invalid_node_types():
    """Test converting with invalid node types"""
    parser = GrammarParser()
    
    class InvalidTypeNode:
        def __init__(self):
            self.trillions = None
            self.billions = None
            self.millions = None
            self.thousands = None
            self.hundreds = None
            self.tens = None
            self.ordinal = 123  # Invalid type for ordinal
    
    with pytest.raises(ParsingError):
        parser._convert_cardinal(InvalidTypeNode())


def test_convert_cardinal_with_invalid_node_attributes():
    """Test converting with invalid node attributes"""
    parser = GrammarParser()
    
    class InvalidAttributeNode:
        def __init__(self):
            self.trillions = None
            self.billions = None
            self.millions = None
            self.thousands = None
            self.hundreds = None
            self.tens = type('obj', (), {'t': 'invalid', 'o': None})()  # Invalid value for tens
            self.ordinal = None
    
    with pytest.raises(ParsingError):
        parser._convert_cardinal(InvalidAttributeNode())


def test_convert_cardinal_with_invalid_node_hierarchy():
    """Test converting with invalid node hierarchy"""
    parser = GrammarParser()
    
    class InvalidHierarchyNode:
        def __init__(self):
            self.trillions = type('obj', (), {'t': 'invalid', 'b': None})()  # Invalid value for trillions
            self.billions = type('obj', (), {'b': 'two', 'm': None})()
            self.millions = type('obj', (), {'m': 'three', 't': None})()
            self.thousands = None
            self.hundreds = None
            self.tens = None
            self.ordinal = None
    
    with pytest.raises(ParsingError):
        parser._convert_cardinal(InvalidHierarchyNode())


def test_convert_cardinal_with_invalid_node_combinations():
    """Test converting with invalid node combinations"""
    parser = GrammarParser()
    
    class InvalidCombinationNode:
        def __init__(self):
            self.trillions = None
            self.billions = None
            self.millions = None
            self.thousands = None
            self.hundreds = type('obj', (), {'h': 'invalid', 't': None})()  # Invalid value for hundreds
            self.tens = None
            self.ordinal = None
    
    with pytest.raises(ParsingError):
        parser._convert_cardinal(InvalidCombinationNode())


def test_convert_cardinal_with_invalid_string_input():
    """Test converting with invalid string input"""
    parser = GrammarParser()
    
    # Test with empty string
    with pytest.raises(ParsingError):
        parser.convert_cardinal("")
    
    # Test with whitespace string
    with pytest.raises(ParsingError):
        parser.convert_cardinal("   ")
    
    # Test with invalid word
    with pytest.raises(ParsingError):
        parser.convert_cardinal("invalid")
    
    # Test with mixed valid and invalid words
    with pytest.raises(ParsingError):
        parser.convert_cardinal("one invalid")
    
    # Test with invalid ordinal
    with pytest.raises(ParsingError):
        parser.convert_cardinal("oneth")


def test_convert_cardinal_with_valid_string_input():
    """Test converting with valid string input"""
    parser = GrammarParser()
    
    # Test with single word
    assert parser.convert_cardinal("one").evaluate() == 1
    assert parser.convert_cardinal("twenty").evaluate() == 20
    assert parser.convert_cardinal("hundred").evaluate() == 100
    
    # Test with multiple words
    assert parser.convert_cardinal("twenty one").evaluate() == 21
    assert parser.convert_cardinal("one hundred").evaluate() == 100
    assert parser.convert_cardinal("one hundred twenty").evaluate() == 120
    
    # Test with ordinal
    assert parser.convert_cardinal("first").evaluate() == 1
    assert parser.convert_cardinal("twenty first").evaluate() == 21
    assert parser.convert_cardinal("hundredth").evaluate() == 100


def test_convert_cardinal_with_special_cases():
    """Test converting with special cases"""
    parser = GrammarParser()
    
    # Test with zero
    assert parser.convert_cardinal("zero").evaluate() == 0
    
    # Test with 'and'
    assert parser.convert_cardinal("one hundred and one").evaluate() == 101
    assert parser.convert_cardinal("one thousand and one").evaluate() == 1001
    
    # Test with large numbers
    assert parser.convert_cardinal("one million").evaluate() == 1000000
    assert parser.convert_cardinal("one billion").evaluate() == 1000000000
    assert parser.convert_cardinal("one trillion").evaluate() == 1000000000000


def test_convert_cardinal_with_invalid_combinations():
    """Test converting with invalid combinations"""
    parser = GrammarParser()
    
    # Test with invalid magnitude combinations
    with pytest.raises(ParsingError):
        parser.convert_cardinal("hundred hundred")
    
    with pytest.raises(ParsingError):
        parser.convert_cardinal("thousand thousand")
    
    with pytest.raises(ParsingError):
        parser.convert_cardinal("million million")
    
    # Test with invalid number combinations
    with pytest.raises(ParsingError):
        parser.convert_cardinal("twenty hundred")
    
    with pytest.raises(ParsingError):
        parser.convert_cardinal("ten thousand million")
    
    with pytest.raises(ParsingError):
        parser.convert_cardinal("one two three")


def test_convert_cardinal_with_decimal_numbers():
    """Test converting with decimal numbers"""
    parser = GrammarParser()
    
    # Test with simple decimals
    assert parser.convert_cardinal("one point zero").evaluate() == 1.0
    assert parser.convert_cardinal("zero point five").evaluate() == 0.5
    assert parser.convert_cardinal("three point one four").evaluate() == 3.14
    
    # Test with complex decimals
    assert parser.convert_cardinal("one hundred point zero one").evaluate() == 100.01
    assert parser.convert_cardinal("one thousand point one").evaluate() == 1000.1
    assert parser.convert_cardinal("one million point zero zero one").evaluate() == 1000000.001


def test_convert_cardinal_with_invalid_tree_nodes():
    """Test converting invalid tree nodes"""
    parser = GrammarParser()
    
    class InvalidTreeNode:
        def __init__(self):
            self.trillions = type('obj', (), {'t': None, 'b': None})()
            self.billions = type('obj', (), {'b': None, 'm': None})()
            self.millions = None
            self.thousands = None
            self.hundreds = None
            self.tens = None
            self.ordinal = None
    
    with pytest.raises(ParsingError):
        parser._convert_cardinal(InvalidTreeNode())


def test_convert_cardinal_with_mixed_magnitude_nodes():
    """Test converting mixed magnitude nodes"""
    parser = GrammarParser()
    
    class MixedMagnitudeNode:
        def __init__(self):
            self.trillions = type('obj', (), {'t': 'one', 'b': None})()
            self.billions = type('obj', (), {'b': 'two', 'm': None})()
            self.millions = type('obj', (), {'m': 'three', 't': None})()
            self.thousands = None
            self.hundreds = None
            self.tens = None
            self.ordinal = None
    
    result = parser._convert_cardinal(MixedMagnitudeNode())
    assert result.evaluate() == 1000000000000 + 2000000000 + 3000000


def test_convert_cardinal_with_complex_tree():
    """Test converting complex tree structures"""
    parser = GrammarParser()
    
    class ComplexTreeNode:
        def __init__(self):
            self.trillions = type('obj', (), {'t': 'one', 'b': 'two'})()
            self.billions = type('obj', (), {'b': 'three', 'm': 'four'})()
            self.millions = type('obj', (), {'m': 'five', 't': 'six'})()
            self.thousands = type('obj', (), {'t': 'seven', 'h': 'eight'})()
            self.hundreds = type('obj', (), {'h': 'nine', 't': 'ten'})()
            self.tens = type('obj', (), {'t': 'twenty', 'o': 'one'})()
            self.ordinal = None
    
    result = parser._convert_cardinal(ComplexTreeNode())
    expected = (1 * 1000000000000 + 
               2 * 1000000000 +
               3 * 1000000000 +
               4 * 1000000 +
               5 * 1000000 +
               6 * 1000 +
               7 * 1000 +
               8 * 100 +
               9 * 100 +
               10 +
               21)
    assert result.evaluate() == expected


def test_convert_cardinal_with_nested_attributes():
    """Test converting nodes with nested attributes"""
    parser = GrammarParser()
    
    class NestedAttributeNode:
        class InnerNode:
            def __init__(self):
                self.t = "twenty"
                self.o = "one"
                self.trillions = None
                self.billions = None
                self.millions = None
                self.thousands = None
                self.hundreds = None
                self.tens = None
                self.ordinal = None
        
        def __init__(self):
            self.inner = self.InnerNode()
            self.trillions = None
            self.billions = None
            self.millions = None
            self.thousands = None
            self.hundreds = None
            self.tens = self.inner
            self.ordinal = None
    
    result = parser._convert_cardinal(NestedAttributeNode())
    assert result.evaluate() == 21


def test_convert_cardinal_with_invalid_decimal_format():
    """Test converting invalid decimal formats"""
    parser = GrammarParser()
    
    # Test with missing whole number
    with pytest.raises(ParsingError):
        parser.convert_cardinal("point one")
    
    # Test with missing fraction
    with pytest.raises(ParsingError):
        parser.convert_cardinal("one point")
    
    # Test with invalid fraction
    with pytest.raises(ParsingError):
        parser.convert_cardinal("one point invalid")
    
    # Test with multiple points
    with pytest.raises(ParsingError):
        parser.convert_cardinal("one point two point three")


def test_convert_cardinal_with_invalid_ordinal_format():
    """Test converting invalid ordinal formats"""
    parser = GrammarParser()
    
    # Test with invalid ordinal words
    with pytest.raises(ParsingError):
        parser.convert_cardinal("oneth")
    
    # Test with mixed ordinal and cardinal
    with pytest.raises(ParsingError):
        parser.convert_cardinal("twenty oneth")
    
    # Test with invalid ordinal combinations
    with pytest.raises(ParsingError):
        parser.convert_cardinal("first hundred")
    
    # Test with repeated ordinals
    with pytest.raises(ParsingError):
        parser.convert_cardinal("first second")
