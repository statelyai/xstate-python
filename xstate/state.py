from typing import Any, Dict


class State:
    value: str
    context: Dict[str, Any]

    def __init__(self, value: str, context: Dict[str, Any]):
        self.value = value
        self.context = context
