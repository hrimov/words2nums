from typing import List

from words2nums.core.parser import Parser
from words2nums.locales.english.tokenizer import (
    ORDINAL_TO_CARDINAL_MAP,
    WORD_TO_VALUE_MAP,
    MAGNITUDE_MAP, PUNCTUATION_TOKENS, FLOAT_DIVIDER,
    ORDINAL_MAGNITUDE_TOKENS,
    HYPHEN,
)
from words2nums.locales.english.tree import (
    NumberNode, DigitNode, MagnitudeNode,
    CompoundNode, DecimalNode, OrdinalNode,
    EnglishTreeBuilder
)


class EnglishParser(Parser):
    def __init__(self):
        self.tree_builder = EnglishTreeBuilder()

    def parse(self, tokens: List[str]) -> NumberNode:
        return self._parse_number(tokens)

    def _parse_number(self, tokens: List[str]) -> NumberNode:
        if not tokens:
            return DigitNode(0)

        # Handle decimal numbers
        if FLOAT_DIVIDER in tokens:
            point_idx = tokens.index(FLOAT_DIVIDER)
            whole = self._parse_number(tokens[:point_idx])
            fraction = self._parse_fraction(tokens[point_idx + 1:])
            return DecimalNode(whole=whole, fraction=fraction)

        # Handle ordinal numbers
        last_token = tokens[-1]
        if last_token in ORDINAL_TO_CARDINAL_MAP or HYPHEN in last_token:
            if last_token in ORDINAL_MAGNITUDE_TOKENS:
                if len(tokens) > 1:
                    base = self._parse_simple_number(tokens[:-1])
                    magnitude = MAGNITUDE_MAP[last_token[:-2]]
                    return OrdinalNode(MagnitudeNode(base=base, multiplier=magnitude))
                return OrdinalNode(DigitNode(ORDINAL_TO_CARDINAL_MAP[last_token]))
            elif HYPHEN in last_token:
                t1, t2 = last_token.split(HYPHEN)
                if t1 in WORD_TO_VALUE_MAP and t2 in ORDINAL_TO_CARDINAL_MAP:
                    base = self._parse_simple_number([t1])
                    return OrdinalNode(
                        CompoundNode(
                            [base, DigitNode(ORDINAL_TO_CARDINAL_MAP[t2] % 10)]
                        )
                    )
            else:
                # Handle cases like "hundred first", "thousand first"
                if len(tokens) > 1:
                    base = self._parse_simple_number(tokens[:-1])
                    ordinal_value = ORDINAL_TO_CARDINAL_MAP[last_token]
                    if ordinal_value < 100:  # For cases like "twenty first"
                        return OrdinalNode(
                            CompoundNode([base, DigitNode(ordinal_value % 10)])
                        )
                    else:
                        return OrdinalNode(
                            CompoundNode([base, DigitNode(ordinal_value)])
                        )
                return OrdinalNode(DigitNode(ORDINAL_TO_CARDINAL_MAP[last_token]))

        return self._parse_simple_number(tokens)

    def _parse_simple_number(self, tokens: List[str]) -> NumberNode:
        """Parse tokens into a number tree
        
        A basic number is either:
        - A single digit/value (e.g., "one", "twenty")
        - A compound of digits and tens (e.g., "twenty three")
        - A sequence of magnitudes (e.g., "one hundred", "two million")
        """
        # TODO (hrimov): move it to the tree parsing logic to reduce +1 traversal
        tokens = [token for token in tokens if token not in PUNCTUATION_TOKENS]
        return self.tree_builder.build_tree(tokens)

    # noinspection PyMethodMayBeStatic
    def _parse_fraction(self, tokens: List[str]) -> List[DigitNode]:
        """Parse the fractional part after 'point'"""
        result = []
        for token in tokens:
            if token in WORD_TO_VALUE_MAP:
                result.append(DigitNode(WORD_TO_VALUE_MAP[token]))
            elif token in MAGNITUDE_MAP:
                # Skip magnitude words in decimal part
                continue
        return result
