from __future__ import annotations
from typing import Any, Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    from xstate.action import Action


class State:
    value: str
    context: Dict[str, Any]
    actions: List[Action]

    def __init__(self, value: str, context: Dict[str, Any], actions: List[Action] = []):
        self.value = value
        self.context = context
        self.actions = actions

    def __repr__(self):
        return repr(
            {"value": self.value, "context": self.context, "actions": self.actions,}
        )

