from typing import List, Optional, Union, cast
from words2nums.locales.english.tree import (
    NumberNode, DigitNode, MagnitudeNode,
    CompoundNode, DecimalNode, OrdinalNode
)


class GrammarParser:

    def _make_trillions(self, t: NumberNode, b: Optional[NumberNode]) -> NumberNode:
        trillion_node = MagnitudeNode(base=t, multiplier=1_000_000_000_000)
        if b is None:
            return trillion_node
        return CompoundNode([trillion_node, cast(NumberNode, b)])

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
        return OrdinalNode(n)

    def _make_float(self, n: NumberNode, d: List[DigitNode]) -> NumberNode:
        return DecimalNode(whole=n, fraction=d)

    def _extend_decimal(self, d: DigitNode, more: List[DigitNode]) -> List[DigitNode]:
        return [d] + more
