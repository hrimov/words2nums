import pytest


@pytest.mark.parametrize("input_text, expected", [
    ("zero", 0),
    ("one", 1),
    ("twenty one", 21),
    ("one hundred", 100),
    ("one thousand", 1000),
    ("seven hundred and twenty three", 723),
    ("one thousand three hundred forty five", 1345),
    ("two thousand three hundred forty five", 2345),
    ("one million two hundred thirty four thousand five hundred sixty seven", 1234567)
])
def test_cardinal_numbers(converter, input_text, expected):
    result = converter.convert(input_text)
    assert result == expected
    assert isinstance(result, int)


@pytest.mark.parametrize("input_text, expected", [
    ("first", 1),
    ("second", 2),
    ("twenty-first", 21),
    ("hundredth", 100),
    ("one hundredth", 100),
    ("one hundred first", 101),
    ("one hundred twenty third", 123),
    ("one thousandth", 1_000),
    ("one thousand first", 1_001),
    ("millionth", 1_000_000),
    ("one millionth", 1_000_000),
    ("one million first", 1_000_001),
    ("two hundredth", 200),
    ("two hundred first", 201),
    ("two hundred twenty third", 223),
    ("two thousandth", 2_000),
    ("two thousand first", 2_001),
    ("two millionth", 2_000_000),
    ("two million first", 2_000_001),
])
def test_ordinal_numbers(converter, input_text, expected):
    result = converter.convert(input_text)
    assert result == expected
    assert isinstance(result, int)


@pytest.mark.parametrize("input_text, expected", [
    ("one point zero", 1.0),
    ("zero point five", 0.5),
    ("three point one four", 3.14),
    (
            "three point one four one five nine two six five three five "
            "eight nine seven nine three two three eight four six two six "
            "four three three eight three two seven nine five",
            3.1415926535897932384626433832795,
    ),
    ("one hundred twenty three point four five six", 123.456),
    ("one thousand two hundred thirty four point five six", 1234.56),
    ("one million one thousand two hundred thirty four point five six", 1_001_234.56),
])
def test_floating_point_numbers(converter, input_text, expected):
    result = converter.convert(input_text)
    assert result == expected
    assert isinstance(result, float)


@pytest.mark.parametrize("input_text, expected", [
    ("and one", 1),
    ("one hundred and one", 101),
    ("twenty-third point one", 23.1),
    ("three million point one", 3000000.1),
    ("ten thousand point one hundred", 10000.1)
])
def test_mixed_scenarios(converter, input_text, expected):
    result = converter.convert(input_text)
    assert result == expected
    assert isinstance(result, float if "point" in input_text else int)


@pytest.mark.parametrize("input_text, expected", [
    ("zero", True),
    ("one", True),
    ("twenty one", True),
    ("one hundred", True),
    ("one thousand", True),
    ("seven hundred and twenty three", True),
    ("one thousand three hundred forty five", True),
    ("two thousand three hundred forty five", True),
    ("one million two hundred thirty four thousand five hundred sixty seven", True),
    ("first", True),
    ("second", True),
    ("twenty-first", True),
    ("hundredth", True),
    ("one hundredth", True),
    ("one hundred first", True),
    ("one hundred twenty third", True),
    ("one thousandth", True),
    ("one thousand first", True),
    ("millionth", True),
    ("one millionth", True),
    ("one million first", True),
    ("two hundredth", True),
    ("two hundred first", True),
    ("two hundred twenty third", True),
    ("two thousandth", True),
    ("two thousand first", True),
    ("two millionth", True),
    ("two million first", True),
    ("one point zero", True),
    ("zero point five", True),
    ("three point one four", True),
    (
            "three point one four one five nine two six five three five "
            "eight nine seven nine three two three eight four six two six "
            "four three three eight three two seven nine five",
            True,
    ),
    ("one hundred twenty three point four five six", True),
    ("one thousand two hundred thirty four point five six", True),
    ("one million one thousand two hundred thirty four point five six", True),
    ("one hundred and one", True),
    ("twenty-third point one", True),
    ("three million point one", True),
    ("ten thousand point one hundred", True)
])
def test_validate_text_correct(tokenizer, input_text, expected):
    assert tokenizer.validate(input_text) == expected


@pytest.mark.parametrize("input_text, expected", [
    ("some text", False),
    ("one two text", False),
])
def test_validate_text_incorrect(tokenizer, input_text, expected):
    assert tokenizer.validate(input_text) == expected
