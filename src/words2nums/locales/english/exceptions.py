from dataclasses import dataclass

from words2nums.core.exceptions import EvaluationError


@dataclass(eq=False)
class UnknownNodeError(EvaluationError):
    """Raised when encountering an unknown node type during evaluation"""

    def __init__(self, node_type: str):
        super().__init__(f"Unknown node type: {node_type}")
