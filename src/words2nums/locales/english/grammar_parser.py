from typing import List, Optional, Union, cast, Any
from words2nums.locales.english.tree import (
    NumberNode, DigitNode, MagnitudeNode,
    CompoundNode, DecimalNode, OrdinalNode
)
from words2nums.locales.english.tokenizer import (
    PUNCTUATION_TOKENS,
    WORD_TO_VALUE_MAP,
    ORDINAL_TO_CARDINAL_MAP,
    MAGNITUDE_MAP,
    FLOAT_DIVIDER
)
from words2nums.core.exceptions import ParsingError


class GrammarParser:

    def _make_trillions(self, t: NumberNode, b: Optional[NumberNode]) -> NumberNode:
        trillion_node = MagnitudeNode(base=t, multiplier=1_000_000_000_000)
        if b is None:
            return trillion_node
        return CompoundNode([trillion_node, b])

    def _make_billions(self, b: NumberNode, m: Optional[NumberNode]) -> NumberNode:
        billion_node = MagnitudeNode(base=b, multiplier=1_000_000_000)
        if m is None:
            return billion_node
        return CompoundNode([billion_node, cast(NumberNode, m)])

    def _make_millions(self, m: NumberNode, t: Optional[NumberNode]) -> NumberNode:
        million_node = MagnitudeNode(base=m, multiplier=1_000_000)
        if t is None:
            return million_node
        return CompoundNode([million_node, cast(NumberNode, t)])

    def _make_thousands(self, t: NumberNode, h: Optional[NumberNode]) -> NumberNode:
        thousand_node = MagnitudeNode(base=t, multiplier=1_000)
        if h is None:
            return thousand_node
        return CompoundNode([thousand_node, cast(NumberNode, h)])

    def _make_hundreds(self, h: Union[int, NumberNode], t: Optional[NumberNode]) -> NumberNode:
        if isinstance(h, int):
            h = DigitNode(h)
        hundred_node = MagnitudeNode(base=h, multiplier=100)
        if t is None:
            return hundred_node
        return CompoundNode([hundred_node, cast(NumberNode, t)])

    def _make_tens(self, t: NumberNode, o: Optional[NumberNode]) -> NumberNode:
        if o is None:
            return t
        return CompoundNode([t, cast(NumberNode, o)])

    def _make_ordinal(self, n: NumberNode) -> NumberNode:
        if not isinstance(n, NumberNode):
            raise ParsingError(f"Expected NumberNode, got {type(n)}")
        return OrdinalNode(n)

    def _make_float(self, n: NumberNode, d: List[DigitNode]) -> NumberNode:
        if not isinstance(n, NumberNode):
            raise ParsingError(f"Expected NumberNode for whole part, got {type(n)}")
        if not isinstance(d, list) or not all(isinstance(x, DigitNode) for x in d):
            raise ParsingError("Expected list of DigitNode for fraction part")
        return DecimalNode(whole=n, fraction=d)

    def _extend_decimal(self, d: DigitNode, more: List[DigitNode]) -> List[DigitNode]:
        return [d] + more

    def _convert_number_to_word(self, number: int) -> str:
        """Convert a number back to its word representation"""
        for word, value in WORD_TO_VALUE_MAP.items():
            if value == number:
                return word
        raise ParsingError(f"Cannot convert number {number} to word")

    def convert_cardinal(self, text: str) -> NumberNode:
        """Public wrapper for _convert_cardinal"""
        # Handle string input
        if isinstance(text, str):
            if not text:
                raise ParsingError("Empty string is not a valid number")
            
            # Try to split into tokens first
            tokens = text.split()
            if tokens:
                # If we have tokens, process them through tree builder
                tokens = [token for token in tokens if token not in PUNCTUATION_TOKENS]
                if not tokens:
                    raise ParsingError("No valid tokens found")
                
                # Check if all tokens are valid
                invalid_tokens = []
                for token in tokens:
                    # Try to convert numeric tokens to words
                    if token.isdigit():
                        try:
                            token = self._convert_number_to_word(int(token))
                        except ParsingError:
                            invalid_tokens.append(token)
                            continue
                    
                    # If token is ordinal and not the only token, treat it as cardinal
                    if len(tokens) > 1 and token in ORDINAL_TO_CARDINAL_MAP:
                        continue
                    
                    if (token not in WORD_TO_VALUE_MAP and 
                        token not in ORDINAL_TO_CARDINAL_MAP and
                        token not in MAGNITUDE_MAP and
                        token not in PUNCTUATION_TOKENS and
                        token != FLOAT_DIVIDER):
                        invalid_tokens.append(token)
                if invalid_tokens:
                    raise ParsingError(f"Invalid tokens found: {invalid_tokens}")
                
                from words2nums.locales.english.tree import EnglishTreeBuilder
                tree_builder = EnglishTreeBuilder()
                result = tree_builder.build_tree(tokens)
                if isinstance(result, OrdinalNode):
                    return result.number
                return result
            else:
                # If single word, try direct conversion
                if text in ORDINAL_TO_CARDINAL_MAP:
                    return DigitNode(ORDINAL_TO_CARDINAL_MAP[text])
                elif text in WORD_TO_VALUE_MAP:
                    return DigitNode(WORD_TO_VALUE_MAP[text])
                raise ParsingError(f"Unknown word: {text}")
            
        # Handle node input
        return self._convert_cardinal(text)

    def convert_ordinal(self, text: str) -> NumberNode:
        """Convert ordinal number text to NumberNode"""
        if text in ORDINAL_TO_CARDINAL_MAP:
            return OrdinalNode(DigitNode(ORDINAL_TO_CARDINAL_MAP[text]))
        raise ParsingError(f"Unknown ordinal: {text}")
        
    def make_ordinal(self, node: NumberNode) -> NumberNode:
        """Public wrapper for _make_ordinal"""
        return self._make_ordinal(node)
        
    def make_float(self, whole: NumberNode, fraction: List[DigitNode]) -> NumberNode:
        """Public wrapper for _make_float"""
        return self._make_float(whole, fraction)

    def _convert_cardinal(self, node: Any) -> NumberNode:
        """Convert cardinal number node from grammar"""
        # Handle string nodes
        if isinstance(node, str):
            if node in WORD_TO_VALUE_MAP:
                return DigitNode(WORD_TO_VALUE_MAP[node])
            elif node in ORDINAL_TO_CARDINAL_MAP:
                return OrdinalNode(DigitNode(ORDINAL_TO_CARDINAL_MAP[node]))
            raise ParsingError(f"Unknown word: {node}")

        # Handle tree nodes
        if hasattr(node, 'trillions') and node.trillions is not None:
            tril = self._convert_cardinal(node.trillions.t)
            bil: Optional[NumberNode] = None
            if hasattr(node.trillions, 'b') and node.trillions.b is not None:
                b = self._convert_cardinal(node.trillions.b)
                bil = MagnitudeNode(base=b, multiplier=1_000_000_000)
            return self._make_trillions(tril, bil)

        if hasattr(node, 'billions') and node.billions is not None:
            bil = self._convert_cardinal(node.billions.b)
            mil: Optional[NumberNode] = None
            if hasattr(node.billions, 'm') and node.billions.m is not None:
                m = self._convert_cardinal(node.billions.m)
                mil = MagnitudeNode(base=m, multiplier=1_000_000)
            return self._make_billions(bil, mil)

        if hasattr(node, 'millions') and node.millions is not None:
            mil = self._convert_cardinal(node.millions.m)
            thou: Optional[NumberNode] = None
            if hasattr(node.millions, 't') and node.millions.t is not None:
                t = self._convert_cardinal(node.millions.t)
                thou = MagnitudeNode(base=t, multiplier=1_000)
            return self._make_millions(mil, thou)

        if hasattr(node, 'thousands') and node.thousands is not None:
            thou = self._convert_cardinal(node.thousands.t)
            hund: Optional[NumberNode] = None
            if hasattr(node.thousands, 'h') and node.thousands.h is not None:
                h = self._convert_cardinal(node.thousands.h)
                hund = MagnitudeNode(base=h, multiplier=100)
            return self._make_thousands(thou, hund)

        if hasattr(node, 'hundreds') and node.hundreds is not None:
            hund = self._convert_cardinal(node.hundreds.h)
            tens: Optional[NumberNode] = None
            if hasattr(node.hundreds, 't') and node.hundreds.t is not None:
                tens = self._convert_cardinal(node.hundreds.t)
            return self._make_hundreds(hund, tens)

        if hasattr(node, 'tens') and node.tens is not None:
            tens = self._convert_cardinal(node.tens.t)
            ones: Optional[NumberNode] = None
            if hasattr(node.tens, 'o') and node.tens.o is not None:
                ones = self._convert_cardinal(node.tens.o)
            return self._make_tens(tens, ones)

        # Handle direct t and o attributes
        if hasattr(node, 't'):
            tens = self._convert_cardinal(node.t)
            ones: Optional[NumberNode] = None
            if hasattr(node, 'o') and node.o is not None:
                ones = self._convert_cardinal(node.o)
            return self._make_tens(tens, ones)

        # Handle unknown node types
        raise ParsingError(f"Unknown node type: {type(node)}")

    def extend_decimal(self, d: DigitNode, more: List[DigitNode]) -> List[DigitNode]:
        """Public wrapper for _extend_decimal"""
        if not isinstance(d, DigitNode):
            raise ParsingError(f"Expected DigitNode for first digit, got {type(d)}")
        if not isinstance(more, list) or not all(isinstance(x, DigitNode) for x in more):
            raise ParsingError("Expected list of DigitNode for more digits")
        return self._extend_decimal(d, more)
