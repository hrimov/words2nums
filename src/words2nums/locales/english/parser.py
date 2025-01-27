from typing import List, Union, Optional
from pathlib import Path
import os

from words2nums.core.parser import Parser
from words2nums.core.exceptions import ParsingError
from words2nums.locales.english.grammar_parser import GrammarParser
from words2nums.locales.english.tree import (
    NumberNode, DigitNode, EnglishTreeBuilder, DecimalNode,
    OrdinalNode, MagnitudeNode, CompoundNode
)
from words2nums.locales.english.tokenizer import (
    ORDINAL_TO_CARDINAL_MAP,
    WORD_TO_VALUE_MAP,
    MAGNITUDE_MAP,
    ORDINAL_MAGNITUDE_TOKENS,
    FLOAT_DIVIDER,
    HYPHEN,
    PUNCTUATION_TOKENS,
    VALID_TOKENS,
)
from lark import Lark, Transformer, Token


class EnglishParser(Parser, GrammarParser):
    class NumberTransformer(Transformer):
        def __init__(self, parser: 'EnglishParser') -> None:
            super().__init__()
            self._parser = parser
            
        def start(self, items: List[NumberNode]) -> NumberNode:
            """Root rule - returns the single parsed number"""
            return items[0]
            
        def number(self, items: List[NumberNode]) -> NumberNode:
            """Number rule - passes through the parsed number"""
            return items[0]
            
        def simple_number(self, items: List[Token]) -> NumberNode:
            """Convert simple number (digit, teen, or ten)"""
            text = " ".join(token.value if hasattr(token, 'value') else token for token in items)
            return self._parser.convert_cardinal(text)
            
        def magnitude_number(self, items: List[Union[Token, NumberNode]]) -> NumberNode:
            """Convert number with magnitude (hundred, thousand, etc.)"""
            if len(items) == 1:  # simple_number
                return items[0]
            elif len(items) == 2:  # simple_number MAGNITUDE
                base = items[0]
                magnitude = items[1]
                if not isinstance(magnitude, (Token, str)):
                    raise ParsingError("Magnitude must be a token or string")
                    
                # Convert base number first
                if isinstance(base, NumberNode):
                    base_value = base.evaluate()
                else:
                    base = self._parser.convert_cardinal(base.value if hasattr(base, 'value') else base)
                    base_value = base.evaluate()
                    
                # Then combine with magnitude
                magnitude_text = magnitude.value if hasattr(magnitude, 'value') else magnitude
                if magnitude_text in MAGNITUDE_MAP:
                    return MagnitudeNode(base=DigitNode(base_value), multiplier=MAGNITUDE_MAP[magnitude_text])
                raise ParsingError(f"Unknown magnitude: {magnitude_text}")
                
            elif len(items) == 3:  # number MAGNITUDE number
                first = items[0]
                magnitude = items[1]
                second = items[2]
                
                if not isinstance(magnitude, (Token, str)):
                    raise ParsingError("Magnitude must be a token or string")
                    
                # Convert first number
                if isinstance(first, NumberNode):
                    first_value = first.evaluate()
                else:
                    first = self._parser.convert_cardinal(first.value if hasattr(first, 'value') else first)
                    first_value = first.evaluate()
                    
                # Convert second number
                if isinstance(second, NumberNode):
                    second_value = second.evaluate()
                else:
                    second = self._parser.convert_cardinal(second.value if hasattr(second, 'value') else second)
                    second_value = second.evaluate()
                    
                magnitude_text = magnitude.value if hasattr(magnitude, 'value') else magnitude
                if magnitude_text in MAGNITUDE_MAP:
                    magnitude_node = MagnitudeNode(base=DigitNode(first_value), multiplier=MAGNITUDE_MAP[magnitude_text])
                    if magnitude_text == "hundred":
                        # For hundred, we need to handle the case where the second number is already a magnitude
                        if isinstance(second, MagnitudeNode):
                            return CompoundNode([magnitude_node, second])
                        else:
                            return CompoundNode([magnitude_node, DigitNode(second_value)])
                    else:
                        # For other magnitudes, we need to handle nested magnitudes
                        if isinstance(second, MagnitudeNode):
                            # If second is already a magnitude node, combine them
                            return CompoundNode([magnitude_node, second])
                        else:
                            # Otherwise, create a new magnitude node
                            return CompoundNode([magnitude_node, DigitNode(second_value)])
                raise ParsingError(f"Unknown magnitude: {magnitude_text}")
            
            # Handle unexpected number of items
            raise ParsingError(f"Invalid magnitude number format: {items}")
            
        def cardinal_number(self, items: List[NumberNode]) -> NumberNode:
            """Pass through cardinal number"""
            return items[0]
            
        def ordinal_number(self, items: List[Union[Token, NumberNode]]) -> NumberNode:
            """Convert sequence of words to ordinal number"""
            if len(items) == 1:  # ORDINAL
                if isinstance(items[0], Token):
                    return self._parser.convert_ordinal(items[0].value)
                return self._parser.make_ordinal(items[0])
            else:  # cardinal_number ORDINAL
                if not isinstance(items[0], NumberNode):
                    cardinal = self._parser.convert_cardinal(items[0].value)
                else:
                    cardinal = items[0]
                return self._parser.make_ordinal(cardinal)
            
        def floating_point_number(self, items: List[Union[Token, NumberNode]]) -> NumberNode:
            """Convert to decimal number"""
            # Convert whole part
            first = items[0]
            if isinstance(first, NumberNode):
                whole = first
            else:
                whole = self._parser.convert_cardinal(first.value)

            # Convert fraction part
            second = items[2]
            if isinstance(second, NumberNode):
                fraction_value = str(second.evaluate())
            else:
                # Convert word to number using convert_cardinal
                fraction = self._parser.convert_cardinal(second.value)
                fraction_value = str(fraction.evaluate())
            
            fraction_digits = [DigitNode(int(fraction_value))]
            return self._parser.make_float(whole, fraction_digits)

        def DIGIT(self, token: Token) -> str:
            return token.value
            
        def TEEN(self, token: Token) -> str:
            return token.value
            
        def TEN(self, token: Token) -> str:
            return token.value
            
        def MAGNITUDE(self, token: Token) -> str:
            return token.value
            
        def ORDINAL(self, token: Token) -> str:
            return token.value
            
        def POINT(self, token: Token) -> str:
            return token.value

    def __init__(self) -> None:
        self.tree_builder = EnglishTreeBuilder()
        self._transformer = self.NumberTransformer(self)
        self._grammar_parser: Optional[Lark] = self._init_grammar_parser()

    def _init_grammar_parser(self):
        """Initialize grammar parser"""
        try:
            # Get path to grammar file relative to this file
            current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
            grammar_path = current_dir / 'grammar.gram'
            
            with open(grammar_path) as f:
                grammar = f.read()
                
            return Lark(
                grammar,
                parser='lalr',
                transformer=self._transformer,
                start='start',
                lexer='basic'  # Use basic lexer for simple tokenization
            )
        except (ImportError, FileNotFoundError):
            return None

    def _parse_with_grammar(self, tokens: List[str]) -> NumberNode:
        if self._grammar_parser is None:
            raise NotImplementedError("Grammar parser not available - lark not installed")

        try:
            # Pre-validate and clean tokens
            valid_tokens = []
            is_ordinal = False
            for token in tokens:
                if token in VALID_TOKENS and token not in PUNCTUATION_TOKENS:
                    valid_tokens.append(token)
                elif HYPHEN in token:
                    t1, t2 = token.split(HYPHEN)
                    if t1 in WORD_TO_VALUE_MAP and t2 in ORDINAL_TO_CARDINAL_MAP:
                        # For hyphenated ordinals like "twenty-first", convert to cardinal + ordinal
                        valid_tokens.append(t1)
                        # Convert ordinal to cardinal (e.g., "first" -> "one")
                        cardinal_value = ORDINAL_TO_CARDINAL_MAP[t2]
                        for word, value in WORD_TO_VALUE_MAP.items():
                            if value == cardinal_value:
                                valid_tokens.append(word)
                                is_ordinal = True
                                break
                        
            if not valid_tokens:
                raise ParsingError("No valid tokens found")
            
            # Check if this is a decimal number
            if FLOAT_DIVIDER in valid_tokens:
                point_idx = valid_tokens.index(FLOAT_DIVIDER)
                whole_tokens = valid_tokens[:point_idx]
                fraction_tokens = valid_tokens[point_idx + 1:]
                
                # Parse whole part
                if len(whole_tokens) == 2 and whole_tokens[1] in MAGNITUDE_MAP:
                    base = self.convert_cardinal(whole_tokens[0])
                    whole = MagnitudeNode(base=base, multiplier=MAGNITUDE_MAP[whole_tokens[1]])
                else:
                    whole = self.tree_builder.build_tree(whole_tokens)
                
                # Parse fraction part
                fraction = []
                for token in fraction_tokens:
                    if token in WORD_TO_VALUE_MAP:
                        fraction.append(DigitNode(WORD_TO_VALUE_MAP[token]))
                return DecimalNode(whole=whole, fraction=fraction)
            
            # Check if the last token is an ordinal
            if valid_tokens[-1] in ORDINAL_TO_CARDINAL_MAP:
                is_ordinal = True
                # Convert ordinal to cardinal
                cardinal_value = ORDINAL_TO_CARDINAL_MAP[valid_tokens[-1]]
                for word, value in WORD_TO_VALUE_MAP.items():
                    if value == cardinal_value:
                        valid_tokens[-1] = word
                        break
            
            # Handle magnitude words
            if len(valid_tokens) == 2 and valid_tokens[1] in MAGNITUDE_MAP:
                base = self.convert_cardinal(valid_tokens[0])
                result = MagnitudeNode(base=base, multiplier=MAGNITUDE_MAP[valid_tokens[1]])
                return OrdinalNode(result) if is_ordinal else result
            
            # Handle compound numbers with magnitude
            if len(valid_tokens) > 2 and valid_tokens[1] in MAGNITUDE_MAP:
                base = self.convert_cardinal(valid_tokens[0])
                magnitude_node = MagnitudeNode(base=base, multiplier=MAGNITUDE_MAP[valid_tokens[1]])
                rest = self.tree_builder.build_tree(valid_tokens[2:])
                result = CompoundNode([magnitude_node, rest])
                return OrdinalNode(result) if is_ordinal else result
            
            text = " ".join(valid_tokens)
            tree = self._grammar_parser.parse(text)
            if not isinstance(tree, NumberNode):
                raise ParsingError("Grammar parser returned invalid type")
            
            # If the original input was a hyphenated ordinal or ended with an ordinal, make sure the result is ordinal
            if is_ordinal:
                return OrdinalNode(tree)
            
            return tree
        except Exception as e:
            raise ParsingError(f"Grammar parsing failed: {str(e)}")

    def parse(self, tokens: List[str]) -> NumberNode:
        """Parse tokens into a number tree
        
        First tries to use grammar parser, falls back to existing parser if grammar parsing fails.
        """
        if not tokens:
            return DigitNode(0)

        if any(not token.strip() for token in tokens):
            raise ParsingError("Empty or whitespace tokens are not allowed")

        # Handle decimal numbers with ordinal parts
        if FLOAT_DIVIDER in tokens:
            point_idx = tokens.index(FLOAT_DIVIDER)
            whole_tokens = tokens[:point_idx]
            fraction_tokens = tokens[point_idx + 1:]

            # Parse whole part
            if len(whole_tokens) == 1 and HYPHEN in whole_tokens[0]:
                t1, t2 = whole_tokens[0].split(HYPHEN)
                if t1 in WORD_TO_VALUE_MAP and t2 in ORDINAL_TO_CARDINAL_MAP:
                    base = DigitNode(WORD_TO_VALUE_MAP[t1])
                    ordinal_value = ORDINAL_TO_CARDINAL_MAP[t2]
                    if ordinal_value < 10:
                        whole = OrdinalNode(CompoundNode([base, DigitNode(ordinal_value % 10)]))
                    else:
                        whole = OrdinalNode(base)
                else:
                    whole = self.tree_builder.build_tree(whole_tokens)
            else:
                whole = self.tree_builder.build_tree(whole_tokens)

            # Parse fraction part
            fraction = []
            for token in fraction_tokens:
                if token in WORD_TO_VALUE_MAP:
                    fraction.append(DigitNode(WORD_TO_VALUE_MAP[token]))
            return DecimalNode(whole=whole, fraction=fraction)

        # Handle single ordinal token
        if len(tokens) == 1:
            if tokens[0] in ORDINAL_TO_CARDINAL_MAP:
                return OrdinalNode(DigitNode(ORDINAL_TO_CARDINAL_MAP[tokens[0]]))
            elif HYPHEN in tokens[0]:
                t1, t2 = tokens[0].split(HYPHEN)
                if t1 in WORD_TO_VALUE_MAP and t2 in ORDINAL_TO_CARDINAL_MAP:
                    base = DigitNode(WORD_TO_VALUE_MAP[t1])
                    ordinal_value = ORDINAL_TO_CARDINAL_MAP[t2]
                    if ordinal_value < 10:
                        return OrdinalNode(CompoundNode([base, DigitNode(ordinal_value % 10)]))
                    return OrdinalNode(base)

        # Check if this is a compound ordinal number (e.g. "twenty first")
        if len(tokens) > 1 and tokens[-1] in ORDINAL_TO_CARDINAL_MAP:
            return self._parse_number(tokens)

        invalid_tokens = []
        for token in tokens:
            if HYPHEN in token:
                t1, t2 = token.split(HYPHEN)
                if not (
                        (t1 in WORD_TO_VALUE_MAP and t2 in ORDINAL_TO_CARDINAL_MAP) or
                        token in VALID_TOKENS
                ):
                    invalid_tokens.append(token)
            elif token not in VALID_TOKENS:
                invalid_tokens.append(token)

        if invalid_tokens:
            raise ParsingError(f"Invalid tokens found: {invalid_tokens}")

        try:
            return self.tree_builder.build_tree(tokens)
        except Exception:
            return self._parse_number(tokens)

    def _parse_number(self, tokens: List[str]) -> NumberNode:
        """Legacy parser implementation"""
        if not tokens:
            return DigitNode(0)

        if FLOAT_DIVIDER in tokens:
            point_idx = tokens.index(FLOAT_DIVIDER)
            whole = self._parse_number(tokens[:point_idx])
            fraction = self._parse_fraction(tokens[point_idx + 1:])
            return DecimalNode(whole=whole, fraction=fraction)

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
                if len(tokens) > 1:
                    base = self._parse_simple_number(tokens[:-1])
                    ordinal_value = ORDINAL_TO_CARDINAL_MAP[last_token]
                    if ordinal_value < 10:
                        return OrdinalNode(
                            CompoundNode([base, DigitNode(ordinal_value)])
                        )
                    return OrdinalNode(base)
                return OrdinalNode(DigitNode(ORDINAL_TO_CARDINAL_MAP[last_token]))

        return self._parse_simple_number(tokens)

    def _parse_simple_number(self, tokens: List[str]) -> NumberNode:
        """Parse basic numbers without magnitude words"""
        # Remove punctuation tokens
        tokens = [token for token in tokens if token not in PUNCTUATION_TOKENS]
        
        # Handle single ordinal token
        if len(tokens) == 1 and tokens[0] in ORDINAL_TO_CARDINAL_MAP:
            return OrdinalNode(DigitNode(ORDINAL_TO_CARDINAL_MAP[tokens[0]]))
        
        # Handle compound ordinal numbers
        if tokens and tokens[-1] in ORDINAL_TO_CARDINAL_MAP:
            base = self.tree_builder.build_tree(tokens[:-1])
            return OrdinalNode(base)
        
        # Handle hyphenated ordinal numbers
        if len(tokens) == 1 and HYPHEN in tokens[0]:
            t1, t2 = tokens[0].split(HYPHEN)
            if t1 in WORD_TO_VALUE_MAP and t2 in ORDINAL_TO_CARDINAL_MAP:
                base = DigitNode(WORD_TO_VALUE_MAP[t1])
                return OrdinalNode(CompoundNode([base, DigitNode(ORDINAL_TO_CARDINAL_MAP[t2] % 10)]))
        
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

    def convert_cardinal(self, text: str) -> NumberNode:
        """Convert cardinal number text to NumberNode"""
        if text in WORD_TO_VALUE_MAP:
            return DigitNode(WORD_TO_VALUE_MAP[text])
        elif text in MAGNITUDE_MAP:
            return MagnitudeNode(base=DigitNode(1), multiplier=MAGNITUDE_MAP[text])
        else:
            # Try to parse as compound number
            tokens = text.split()
            if len(tokens) > 1:
                return self.tree_builder.build_tree(tokens)
            raise ParsingError(f"Unknown cardinal: {text}")

    def convert_ordinal(self, text: str) -> NumberNode:
        """Convert ordinal number text to NumberNode"""
        if text in ORDINAL_TO_CARDINAL_MAP:
            return OrdinalNode(DigitNode(ORDINAL_TO_CARDINAL_MAP[text]))
        raise ParsingError(f"Unknown ordinal: {text}")

    def make_ordinal(self, number: NumberNode) -> NumberNode:
        """Convert cardinal number to ordinal"""
        return OrdinalNode(number)

    def make_float(self, whole: NumberNode, fraction: List[DigitNode]) -> NumberNode:
        """Create decimal number from whole and fraction parts"""
        return DecimalNode(whole=whole, fraction=fraction)
