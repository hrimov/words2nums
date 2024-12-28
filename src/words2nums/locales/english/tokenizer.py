from typing import List

from words2nums.core.tokenizer import Tokenizer


ORDINAL_TO_CARDINAL_MAP = {
    "first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5,
    "sixth": 6, "seventh": 7, "eighth": 8, "ninth": 9, "tenth": 10,
    "eleventh": 11, "twelfth": 12, "thirteenth": 13, "fourteenth": 14,
    "fifteenth": 15, "sixteenth": 16, "seventeenth": 17, "eighteenth": 18,
    "nineteenth": 19, "twentieth": 20, "thirtieth": 30, "fortieth": 40,
    "fiftieth": 50, "sixtieth": 60, "seventieth": 70, "eightieth": 80,
    "ninetieth": 90, "hundredth": 100, "thousandth": 1_000, "millionth": 1_000_000
}


WORD_TO_VALUE_MAP = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
    "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
    "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
    "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17,
    "eighteen": 18, "nineteen": 19, "twenty": 20,
    "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60,
    "seventy": 70, "eighty": 80, "ninety": 90
}


MAGNITUDE_MAP = {
    "hundred": 100,
    "thousand": 1000,
    "million": 1_000_000
}


ORDINAL_MAGNITUDE_TOKENS = {"hundredth", "thousandth", "millionth"}
PUNCTUATION_TOKENS = {"and"}


HYPHEN = "-"
FLOAT_DIVIDER = "point"


VALID_TOKENS = set(
    list(ORDINAL_TO_CARDINAL_MAP) +
    list(WORD_TO_VALUE_MAP) +
    list(MAGNITUDE_MAP) +
    [FLOAT_DIVIDER]
) | PUNCTUATION_TOKENS


class EnglishTokenizer(Tokenizer):
    def tokenize(self, text: str) -> List[str]:
        tokens = text.lower().split(" ")

        for idx, token in enumerate(tokens):
            if HYPHEN in token:
                t1, t2 = token.split(HYPHEN)
                tokens[idx] = t1
                tokens.insert(idx + 1, t2)
        return tokens

    def validate(self, text: str) -> bool:
        tokens = self.tokenize(text)
        return all([token in VALID_TOKENS for token in tokens])
