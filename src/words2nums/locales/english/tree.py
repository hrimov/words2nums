import abc
from dataclasses import dataclass
from typing import List, Sequence

from words2nums.core.types import NumberData, ReturnValue
from words2nums.locales.english.tokenizer import (
    WORD_TO_VALUE_MAP,
    MAGNITUDE_MAP,
)


@dataclass
class NumberNode(NumberData):
    """Base class for all nodes in number tree"""
    
    def evaluate(self) -> ReturnValue:
        """Evaluate this node to get its numeric value"""
        from words2nums.locales.english.evaluator import EnglishEvaluator
        evaluator = EnglishEvaluator()
        return evaluator.evaluate(self)


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


class TreeBuilder(abc.ABC):
    """Protocol for building number tree"""

    @abc.abstractmethod
    def build_tree(self, tokens: List[str]) -> NumberNode: ...

    @abc.abstractmethod
    def parse_basic_number(self, tokens: List[str]) -> NumberNode: ...


class EnglishTreeBuilder(TreeBuilder):
    """Builds tree structures from English number words"""

    def build_tree(self, tokens: List[str]) -> NumberNode:
        """Build a tree from tokens"""
        if not tokens:
            return DigitNode(0)

        # First find the highest magnitude (thousand, million, etc.)
        max_magnitude = 0
        max_magnitude_idx = -1
        
        for i, token in enumerate(tokens):
            if token in MAGNITUDE_MAP and token != "hundred":  # Skip a hundred for now
                magnitude = MAGNITUDE_MAP[token]
                if magnitude > max_magnitude:
                    max_magnitude = magnitude
                    max_magnitude_idx = i

        if max_magnitude_idx != -1:
            # Process highest magnitude first
            left_tokens = tokens[:max_magnitude_idx]
            magnitude_value = MAGNITUDE_MAP[tokens[max_magnitude_idx]]  # Get numeric value
            right_tokens = tokens[max_magnitude_idx + 1:]

            # Handle base number (default to 1 if no left tokens)
            base = self.build_tree(left_tokens) if left_tokens else DigitNode(1)
            magnitude_node = MagnitudeNode(base=base, multiplier=magnitude_value)

            if right_tokens:
                right_node = self.build_tree(right_tokens)
                return CompoundNode([magnitude_node, right_node])

            return magnitude_node

        # Then handle hundreds
        hundred_idx = -1
        for i, token in enumerate(tokens):
            if token == "hundred":
                hundred_idx = i
                break

        if hundred_idx != -1:
            # Process a "hundred" part
            left_tokens = tokens[:hundred_idx]
            right_tokens = tokens[hundred_idx + 1:]
            
            # Handle base number (default to 1 if no left tokens)
            base = self.parse_basic_number(left_tokens) if left_tokens else DigitNode(1)
            hundred_node = MagnitudeNode(base=base, multiplier=100)
            
            if right_tokens:
                right_node = self.parse_basic_number(right_tokens)
                return CompoundNode([hundred_node, right_node])
            return hundred_node

        # Finally handle basic numbers
        return self.parse_basic_number(tokens)

    # noinspection PyMethodMayBeStatic
    def parse_basic_number(self, tokens: List[str]) -> NumberNode:
        """Parse basic numbers without magnitude words"""
        if not tokens:
            return DigitNode(0)

        parts: List[NumberNode] = []
        current_value = 0

        for token in tokens:
            if token in WORD_TO_VALUE_MAP:
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

        # Handle empty parts list
        if not parts:
            return DigitNode(0)
            
        return CompoundNode(parts) if len(parts) > 1 else parts[0]
