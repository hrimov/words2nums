import abc
from dataclasses import dataclass
from typing import List, Sequence, Dict, Union

from words2nums.core.types import NumberData, ReturnValue
from words2nums.locales.english.tokenizer import (
    WORD_TO_VALUE_MAP,
    MAGNITUDE_MAP,
    ORDINAL_TO_CARDINAL_MAP,
    FLOAT_DIVIDER,
    PUNCTUATION_TOKENS
)
from words2nums.core.exceptions import ParsingError


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
        """Build a number tree from tokens"""
        
        if not tokens:
            return DigitNode(0)

        # Handle single ordinal number
        if len(tokens) == 1 and tokens[0] in ORDINAL_TO_CARDINAL_MAP:
            return OrdinalNode(DigitNode(ORDINAL_TO_CARDINAL_MAP[tokens[0]]))

        # Check if the last token is ordinal
        is_ordinal = tokens[-1] in ORDINAL_TO_CARDINAL_MAP

        # Convert ordinal to cardinal if needed
        if is_ordinal:
            # Convert ordinal to cardinal
            cardinal_value = ORDINAL_TO_CARDINAL_MAP[tokens[-1]]
            for word, value in WORD_TO_VALUE_MAP.items():
                if value == cardinal_value:
                    tokens = tokens[:-1] + [word]
                    break

        # Handle decimal numbers
        if FLOAT_DIVIDER in tokens:
            point_idx = tokens.index(FLOAT_DIVIDER)
            whole_tokens = tokens[:point_idx]
            fraction_tokens = tokens[point_idx + 1:]
            
            # Parse whole part
            whole = self.build_tree(whole_tokens)
            
            # Parse fraction part
            fraction = []
            for token in fraction_tokens:
                if token in WORD_TO_VALUE_MAP:
                    fraction.append(DigitNode(WORD_TO_VALUE_MAP[token]))
                else:
                    raise ParsingError(f"Invalid decimal part: {token}")
            
            return DecimalNode(whole=whole, fraction=fraction)

        # Handle magnitude words (hundred, thousand, million, etc.)
        # Process magnitudes from largest to smallest
        magnitudes = sorted(MAGNITUDE_MAP.keys(), key=lambda x: MAGNITUDE_MAP[x], reverse=True)
        
        # Check for consecutive duplicate magnitudes and invalid combinations
        last_magnitude_value = float('inf')
        last_magnitude_group = float('inf')  # Track magnitude groups (millions, thousands, hundreds)
        last_non_magnitude_index = -1  # Track the last non-magnitude word
        last_magnitude_index = -1  # Track the last magnitude word
        last_number_index = -1  # Track the last number word
        last_number_value = 0  # Track the value of the last number
        
        for i in range(len(tokens) - 1):
            # Check for consecutive duplicate magnitudes
            if tokens[i] in MAGNITUDE_MAP and tokens[i] == tokens[i + 1]:
                raise ParsingError(f"Invalid combination: consecutive magnitude '{tokens[i]}'")
            
            # Check for invalid combinations like "twenty hundred"
            if tokens[i] in WORD_TO_VALUE_MAP and tokens[i + 1] in MAGNITUDE_MAP:
                value = WORD_TO_VALUE_MAP[tokens[i]]
                if value >= 20:  # Numbers 20 and above can't be used with magnitudes
                    raise ParsingError(f"Invalid combination: cannot use '{tokens[i]}' with magnitude '{tokens[i + 1]}'")
            
            # Check for consecutive numbers without magnitude words
            if tokens[i] in WORD_TO_VALUE_MAP:
                current_value = WORD_TO_VALUE_MAP[tokens[i]]
                if last_number_index >= 0 and i == last_number_index + 1 and tokens[i + 1] not in MAGNITUDE_MAP:
                    # Allow combinations like "twenty one" where first number is a multiple of 10 and second is less than 10
                    if not (last_number_value % 10 == 0 and last_number_value >= 20 and current_value < 10):
                        raise ParsingError(f"Invalid combination: consecutive numbers without magnitude")
                last_number_index = i
                last_number_value = current_value
            
            # Reset magnitude tracking when we encounter a non-magnitude word
            if tokens[i] not in MAGNITUDE_MAP:
                last_non_magnitude_index = i
                if i > 0 and tokens[i - 1] not in MAGNITUDE_MAP and i < len(tokens) - 1 and tokens[i + 1] in MAGNITUDE_MAP:
                    # Reset magnitude tracking only if we're starting a new number group
                    last_magnitude_value = float('inf')
                    last_magnitude_group = float('inf')
            # Check for invalid magnitude order within the same group
            elif tokens[i] in MAGNITUDE_MAP:
                current_magnitude = MAGNITUDE_MAP[tokens[i]]
                current_group = current_magnitude // 1000 if current_magnitude >= 1000 else 0
                
                # Check if we have a magnitude word after a smaller magnitude in the same group
                if last_magnitude_index >= 0 and i - last_magnitude_index == 2:
                    prev_magnitude = MAGNITUDE_MAP[tokens[last_magnitude_index]]
                    if current_magnitude > prev_magnitude:
                        raise ParsingError(f"Invalid combination: cannot use larger magnitude '{tokens[i]}' after smaller magnitude '{tokens[last_magnitude_index]}'")
                
                # Only check order if we're in the same group and there was no non-magnitude word between
                if current_group == last_magnitude_group and i > last_non_magnitude_index + 1:
                    if current_magnitude >= last_magnitude_value:
                        raise ParsingError(f"Invalid combination: magnitudes in the same group must be in descending order")
                
                last_magnitude_value = current_magnitude
                last_magnitude_group = current_group
                last_magnitude_index = i
        
        # Check the last token
        if tokens[-1] in WORD_TO_VALUE_MAP:
            current_value = WORD_TO_VALUE_MAP[tokens[-1]]
            if last_number_index >= 0 and len(tokens) - 1 == last_number_index + 1:
                # Allow combinations like "twenty one" where first number is a multiple of 10 and second is less than 10
                if not (last_number_value % 10 == 0 and last_number_value >= 20 and current_value < 10):
                    raise ParsingError(f"Invalid combination: consecutive numbers without magnitude")
        elif tokens[-1] in MAGNITUDE_MAP:
            current_magnitude = MAGNITUDE_MAP[tokens[-1]]
            current_group = current_magnitude // 1000 if current_magnitude >= 1000 else 0
            
            # Check if we have a magnitude word after a smaller magnitude in the same group
            if last_magnitude_index >= 0 and len(tokens) - 1 - last_magnitude_index == 2:
                prev_magnitude = MAGNITUDE_MAP[tokens[last_magnitude_index]]
                if current_magnitude > prev_magnitude:
                    raise ParsingError(f"Invalid combination: cannot use larger magnitude '{tokens[-1]}' after smaller magnitude '{tokens[last_magnitude_index]}'")
            
            # Only check order if we're in the same group and there was no non-magnitude word between
            if current_group == last_magnitude_group and len(tokens) - 1 > last_non_magnitude_index + 1:
                if current_magnitude >= last_magnitude_value:
                    raise ParsingError(f"Invalid combination: magnitudes in the same group must be in descending order")
        
        # First find the largest magnitude
        max_magnitude = None
        max_magnitude_idx = -1
        for magnitude in magnitudes:
            if magnitude in tokens:
                max_magnitude = magnitude
                max_magnitude_idx = tokens.index(magnitude)
                break
                
        if max_magnitude is not None:
            # Get the base number (before magnitude)
            if max_magnitude_idx > 0:
                base = self.parse_basic_number(tokens[:max_magnitude_idx])
            else:
                base = DigitNode(1)  # Default to 1 if no base specified

            # Create magnitude node
            magnitude_value = MAGNITUDE_MAP[max_magnitude]
            magnitude_node = MagnitudeNode(base=base, multiplier=magnitude_value)

            # If there are more tokens after magnitude, process them recursively
            if max_magnitude_idx < len(tokens) - 1:
                rest = self.build_tree(tokens[max_magnitude_idx + 1:])
                result = CompoundNode([magnitude_node, rest])
                return OrdinalNode(result) if is_ordinal else result
            
            result = magnitude_node
            return OrdinalNode(result) if is_ordinal else result

        # If no magnitude words found, parse as basic number
        result = self.parse_basic_number(tokens)
        return OrdinalNode(result) if is_ordinal else result

    def parse_basic_number(self, tokens: List[str]) -> NumberNode:
        """Parse basic numbers without magnitude words"""

        if not tokens:
            return DigitNode(0)

        # Handle magnitude words
        for magnitude in MAGNITUDE_MAP:
            if magnitude in tokens:
                idx = tokens.index(magnitude)
                if idx > 0:
                    base = self.parse_basic_number(tokens[:idx])
                else:
                    base = DigitNode(1)
                
                magnitude_node = MagnitudeNode(base=base, multiplier=MAGNITUDE_MAP[magnitude])
                
                if idx < len(tokens) - 1:
                    rest = self.parse_basic_number(tokens[idx + 1:])
                    return CompoundNode([magnitude_node, rest])
                
                return magnitude_node

        parts: List[NumberNode] = []
        current_value = 0

        for token in tokens:
            if token in WORD_TO_VALUE_MAP:
                value = WORD_TO_VALUE_MAP[token]
                if 20 <= value <= 90:  # tens
                    if current_value:
                        parts.append(DigitNode(current_value))
                        current_value = 0
                    parts.append(TensNode(value))
                else:
                    current_value += value
            elif token in ORDINAL_TO_CARDINAL_MAP:
                # If this is part of a compound number, treat it as cardinal
                value = ORDINAL_TO_CARDINAL_MAP[token]
                if 20 <= value <= 90:  # tens
                    if current_value:
                        parts.append(DigitNode(current_value))
                        current_value = 0
                    parts.append(TensNode(value))
                else:
                    current_value += value
            elif token not in PUNCTUATION_TOKENS:
                raise ParsingError(f"Unknown token: {token}")

        if current_value:
            parts.append(DigitNode(current_value))

        if not parts:
            return DigitNode(0)
        elif len(parts) == 1:
            return parts[0]
        else:
            return CompoundNode(parts)
