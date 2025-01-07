from typing import List, Any, Optional
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


class EnglishParser(Parser, GrammarParser):
    def __init__(self):
        self.tree_builder = EnglishTreeBuilder()
        self._grammar_parser = self._init_grammar_parser()

    def parse(self, tokens: List[str]) -> NumberNode:
        """Parse tokens into a number tree
        
        First tries to use grammar parser, falls back to existing parser if grammar parsing fails.
        """
        if not tokens:
            return DigitNode(0)

        if any(not token.strip() for token in tokens):
            raise ParsingError("Empty or whitespace tokens are not allowed")

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
            return self._parse_with_grammar(tokens)
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
                    if ordinal_value < 100:
                        return OrdinalNode(
                            CompoundNode([base, DigitNode(ordinal_value % 10)])
                        )
                    else:
                        return OrdinalNode(
                            CompoundNode([base, DigitNode(ordinal_value)])
                        )
                return OrdinalNode(DigitNode(ORDINAL_TO_CARDINAL_MAP[last_token]))

        return self._parse_simple_number(tokens)

    # noinspection PyMethodMayBeStatic
    def _init_grammar_parser(self):
        """Initialize grammar parser from grammar file"""
        # Get path to grammar file relative to this file
        current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        grammar_path = current_dir / 'grammar.gram'

        try:
            from pegen.build import build_parser_and_generator

            # Generate parser from grammar file
            with open(grammar_path) as f:
                grammar = f.read()
                parser_source = build_parser_and_generator(
                    grammar,
                    grammar_path.name,
                    output_file=None,
                    compile_extension=False,
                )[0]

                # Create module namespace for parser
                namespace = {}
                exec(parser_source, namespace)

                # Return parser class from generated module
                return namespace['GeneratedParser']

        except ImportError:
            # If pegen not installed, always fallback to old parser
            return None

    def _parse_with_grammar(self, tokens: List[str]) -> NumberNode:
        """Parse tokens using formal grammar definition"""
        if self._grammar_parser is None:
            raise NotImplementedError("Grammar parser not available - pegen not installed")

        try:
            # Convert tokens to string that grammar expects
            text = " ".join(tokens)

            # Parse using generated parser
            tree = self._grammar_parser.parse_string(text)
            if tree is None:
                raise ParsingError(f"Failed to parse: {text}")

            return self._convert_parse_tree(tree)
        except Exception as e:
            raise ParsingError(f"Grammar parsing failed: {str(e)}")

    def _convert_parse_tree(self, tree: Any) -> NumberNode:
        """Convert parser's AST to our NumberNode tree"""
        # The tree will match our grammar rules
        if hasattr(tree, 'number'):
            # Handle each grammar rule based on the type of number
            if hasattr(tree.number, 'cardinal_number'):
                return self._convert_cardinal(tree.number.cardinal_number)
            if hasattr(tree.number, 'ordinal_number'):
                return self._make_ordinal(self._convert_cardinal(tree.number.ordinal_number))
            if hasattr(tree.number, 'floating_point_number'):
                whole = self._convert_cardinal(tree.number.floating_point_number.whole)
                fraction = [DigitNode(int(d)) for d in tree.number.floating_point_number.fraction]
                return self._make_float(whole, fraction)

            raise ParsingError(f"Unknown number type in parse tree: {tree.number}")

        # Handle direct number types if not wrapped in 'number' node
        if hasattr(tree, 'cardinal_number'):
            return self._convert_cardinal(tree.cardinal_number)
        if hasattr(tree, 'ordinal_number'):
            return self._make_ordinal(self._convert_cardinal(tree.ordinal_number))
        if hasattr(tree, 'floating_point_number'):
            whole = self._convert_cardinal(tree.floating_point_number.whole)
            fraction = [DigitNode(int(d)) for d in tree.floating_point_number.fraction]
            return self._make_float(whole, fraction)

        raise ParsingError(f"Unknown parse tree node: {tree}")

    def _convert_cardinal(self, node: Any) -> NumberNode:
        """Convert cardinal number node from grammar"""
        if hasattr(node, 'trillions'):
            tril = self._convert_cardinal(node.trillions.t)
            bil: Optional[NumberNode] = None
            if hasattr(node.trillions, 'b'):
                bil = self._convert_cardinal(node.trillions.b)
            return self._make_trillions(tril, bil)
            
        if hasattr(node, 'billions'):
            bil = self._convert_cardinal(node.billions.b)
            mil: Optional[NumberNode] = None
            if hasattr(node.billions, 'm'):
                mil = self._convert_cardinal(node.billions.m)
            return self._make_billions(bil, mil)

        if hasattr(node, 'millions'):
            mil = self._convert_cardinal(node.millions.m)
            thou: Optional[NumberNode] = None
            if hasattr(node.millions, 't'):
                thou = self._convert_cardinal(node.millions.t)
            return self._make_millions(mil, thou)

        if hasattr(node, 'thousands'):
            thou = self._convert_cardinal(node.thousands.t)
            hund: Optional[NumberNode] = None
            if hasattr(node.thousands, 'h'):
                hund = self._convert_cardinal(node.thousands.h)
            return self._make_thousands(thou, hund)

        if hasattr(node, 'hundreds'):
            hund = self._convert_cardinal(node.hundreds.h)
            tens: Optional[NumberNode] = None
            if hasattr(node.hundreds, 't'):
                tens = self._convert_cardinal(node.hundreds.t)
            return self._make_hundreds(hund, tens)

        if hasattr(node, 'tens'):
            tens = self._convert_cardinal(node.tens.t)
            ones: Optional[NumberNode] = None
            if hasattr(node.tens, 'o'):
                ones = self._convert_cardinal(node.tens.o)
            return self._make_tens(tens, ones)
        
        # Base case - single digit/value
        if hasattr(node, 'value'):
            return DigitNode(node.value)
        
        # If we can't handle the node, return zero
        return DigitNode(0)

    def _parse_simple_number(self, tokens: List[str]) -> NumberNode:
        """Parse basic numbers without magnitude words"""
        # Remove punctuation tokens
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
