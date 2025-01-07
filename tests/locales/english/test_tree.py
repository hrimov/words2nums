import pytest
from words2nums.core.exceptions import ParsingError
from words2nums.locales.english.tree import (
    NumberNode, DigitNode, TensNode, MagnitudeNode,
    CompoundNode, DecimalNode, OrdinalNode, EnglishTreeBuilder
)


def test_digit_node():
    node = DigitNode(5)
    assert node.evaluate() == 5


def test_tens_node():
    node = TensNode(20)
    assert node.evaluate() == 20


def test_magnitude_node():
    base = DigitNode(2)
    node = MagnitudeNode(base=base, multiplier=100)
    assert node.evaluate() == 200


def test_compound_node():
    parts = [DigitNode(2), TensNode(20)]
    node = CompoundNode(parts=parts)
    assert node.evaluate() == 22


def test_decimal_node():
    whole = DigitNode(1)
    fraction = [DigitNode(2), DigitNode(3)]
    node = DecimalNode(whole=whole, fraction=fraction)
    assert node.evaluate() == 1.23


def test_ordinal_node():
    number = DigitNode(1)
    node = OrdinalNode(number=number)
    assert node.evaluate() == 1


def test_tree_builder_empty():
    builder = EnglishTreeBuilder()
    result = builder.build_tree([])
    assert isinstance(result, DigitNode)
    assert result.evaluate() == 0


def test_tree_builder_single_digit():
    builder = EnglishTreeBuilder()
    result = builder.build_tree(["one"])
    assert isinstance(result, DigitNode)
    assert result.evaluate() == 1


def test_tree_builder_tens():
    builder = EnglishTreeBuilder()
    result = builder.build_tree(["twenty"])
    assert isinstance(result, TensNode)
    assert result.evaluate() == 20


def test_tree_builder_compound():
    builder = EnglishTreeBuilder()
    result = builder.build_tree(["twenty", "one"])
    assert isinstance(result, CompoundNode)
    assert result.evaluate() == 21


def test_tree_builder_magnitude():
    builder = EnglishTreeBuilder()
    result = builder.build_tree(["one", "hundred"])
    assert isinstance(result, MagnitudeNode)
    assert result.evaluate() == 100


def test_tree_builder_complex_magnitude():
    builder = EnglishTreeBuilder()
    result = builder.build_tree(["one", "hundred", "twenty", "three"])
    assert isinstance(result, CompoundNode)
    assert result.evaluate() == 123


def test_tree_builder_multiple_magnitudes():
    builder = EnglishTreeBuilder()
    result = builder.build_tree(["one", "million", "two", "hundred", "thousand"])
    assert isinstance(result, CompoundNode)
    assert result.evaluate() == 1_200_000


def test_tree_builder_ordinal():
    builder = EnglishTreeBuilder()
    result = builder.build_tree(["first"])
    assert isinstance(result, OrdinalNode)
    assert result.evaluate() == 1


def test_tree_builder_ordinal_with_magnitude():
    builder = EnglishTreeBuilder()
    result = builder.build_tree(["one", "hundred", "and", "twenty", "third"])
    assert isinstance(result, OrdinalNode)
    assert result.evaluate() == 123


def test_tree_builder_decimal():
    builder = EnglishTreeBuilder()
    result = builder.build_tree(["one", "point", "two", "three"])
    assert isinstance(result, DecimalNode)
    assert result.evaluate() == 1.23


def test_tree_builder_decimal_with_magnitude():
    builder = EnglishTreeBuilder()
    result = builder.build_tree(["one", "hundred", "point", "two", "three"])
    assert isinstance(result, DecimalNode)
    assert result.evaluate() == 100.23


def test_tree_builder_invalid_tokens():
    builder = EnglishTreeBuilder()
    with pytest.raises(ParsingError):
        builder.build_tree(["invalid"])


def test_tree_builder_invalid_magnitude():
    builder = EnglishTreeBuilder()
    with pytest.raises(ParsingError):
        builder.build_tree(["one", "invalid"])


def test_tree_builder_invalid_decimal():
    builder = EnglishTreeBuilder()
    with pytest.raises(ParsingError):
        builder.build_tree(["one", "point", "invalid"]) 