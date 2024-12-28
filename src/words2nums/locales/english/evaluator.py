from words2nums.core.evaluator import Evaluator
from words2nums.core.types import ReturnValue, NumberData
from words2nums.locales.english.exceptions import UnknownNodeError
from words2nums.locales.english.tree import (
    NumberNode, DigitNode, TensNode, MagnitudeNode,
    CompoundNode, DecimalNode, OrdinalNode
)


class EnglishEvaluator(Evaluator):
    def evaluate(
            self,
            data: NumberData,
    ) -> ReturnValue:
        if not isinstance(data, NumberNode):
            raise UnknownNodeError(type(data).__name__)

        if isinstance(data, DigitNode):
            return data.value

        if isinstance(data, TensNode):
            return data.value

        if isinstance(data, MagnitudeNode):
            base_value = self.evaluate(data.base)
            return base_value * data.multiplier

        if isinstance(data, CompoundNode):
            return sum(self.evaluate(part) for part in data.parts)

        if isinstance(data, DecimalNode):
            whole_part = self.evaluate(data.whole)
            fraction_part = sum(
                self.evaluate(digit) / (10 ** (i + 1))
                for i, digit in enumerate(data.fraction)
            )
            return float(whole_part + fraction_part)

        if isinstance(data, OrdinalNode):
            return self.evaluate(data.number)

        raise UnknownNodeError(type(data).__name__)
