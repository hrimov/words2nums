import abc
from dataclasses import dataclass
from typing import List, Sequence

from words2nums.core.types import NumberData
from words2nums.locales.english.tokenizer import (
    WORD_TO_VALUE_MAP,
    MAGNITUDE_MAP,
)


@dataclass
class NumberNode(NumberData):
    """Base class for all nodes in number tree"""
    pass


@dataclass
class DigitNode(NumberNode):
    """Represents a simple digit (0-9) or basic number (11-19)"""
    __slots__ = ("value",)
    value: int


@dataclass
class TensNode(NumberNode):
    """Represents numbers like twenty, thirty, etc."""
    __slots__ = ("value",)
    value: int


@dataclass
class MagnitudeNode(NumberNode):
    """Represents multipliers like hundred, thousand, million"""
    __slots__ = ("base", "multiplier",)
    base: NumberNode
    multiplier: int


@dataclass
class CompoundNode(NumberNode):
    """Represents a compound number (e.g., twenty-three)"""
    __slots__ = ("parts",)
    parts: Sequence[NumberNode]


@dataclass
class DecimalNode(NumberNode):
    """Represents a decimal number"""
    __slots__ = ("whole", "fraction",)
    whole: NumberNode
    fraction: List[DigitNode]


@dataclass
class OrdinalNode(NumberNode):
    """Wraps any number node to mark it as ordinal"""
    __slots__ = ("number",)
    number: NumberNode


MAGNITUDE_LEVELS_MAP = {
    'million': 3,
    'thousand': 2,
    'hundred': 1,
    'hundredth': 1,
    'thousandth': 2,
    'millionth': 3
}


class TreeBuilder(abc.ABC):
    """Protocol for building number tree"""

    @abc.abstractmethod
    def build_tree(self, tokens: List[str]) -> NumberNode: ...

    @abc.abstractmethod
    def parse_basic_number(self, tokens: List[str]) -> NumberNode: ...


class EnglishTreeBuilder(TreeBuilder):
    """Builds tree structures from English number words"""

    def build_tree(self, tokens: List[str]) -> NumberNode:
        """Build a tree by recursively processing magnitude levels"""
        max_level = 0
        max_level_idx = -1

        for i, token in enumerate(tokens):
            if token in MAGNITUDE_MAP:
                base_token = token[:-2] if token.endswith('th') else token
                if base_token in MAGNITUDE_LEVELS_MAP:
                    level = MAGNITUDE_LEVELS_MAP[base_token]
                    if level > max_level:
                        max_level = level
                        max_level_idx = i

        if max_level_idx == -1:
            return self.parse_basic_number(tokens)

        left_tokens = tokens[:max_level_idx]
        magnitude = tokens[max_level_idx]
        right_tokens = tokens[max_level_idx + 1:]

        base = self.parse_basic_number(left_tokens) if left_tokens else DigitNode(1)
        magnitude_node = MagnitudeNode(base, MAGNITUDE_MAP[magnitude])

        if right_tokens:
            right_node = self.build_tree(right_tokens)
            return CompoundNode([magnitude_node, right_node])

        return magnitude_node

    # noinspection PyMethodMayBeStatic
    def parse_basic_number(self, tokens: List[str]) -> NumberNode:
        """Parse basic numbers without magnitude words"""
        if not tokens:
            return DigitNode(0)

        if len(tokens) == 1:
            token = tokens[0]
            if token in WORD_TO_VALUE_MAP:
                return DigitNode(WORD_TO_VALUE_MAP[token])
            if token in MAGNITUDE_MAP:
                return MagnitudeNode(DigitNode(1), MAGNITUDE_MAP[token])

        parts: List[NumberNode] = []
        current_value = 0

        for token in tokens:
            if token in MAGNITUDE_MAP:
                if current_value == 0:
                    current_value = 1
                magnitude_node = MagnitudeNode(
                    DigitNode(current_value),
                    MAGNITUDE_MAP[token]
                )
                parts.append(magnitude_node)
                current_value = 0
            elif token in WORD_TO_VALUE_MAP:
                value = WORD_TO_VALUE_MAP[token]
                if 20 <= value <= 90:  # tens
                    if current_value:
                        parts.append(DigitNode(current_value))
                    parts.append(TensNode(value))
                    current_value = 0
                else:
                    current_value += value

        if current_value:
            parts.append(DigitNode(current_value))

        return CompoundNode(parts) if len(parts) > 1 else parts[0]
