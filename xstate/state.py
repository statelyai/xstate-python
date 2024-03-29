from typing import TYPE_CHECKING, Any, Dict, List, Set

from xstate.algorithm import get_state_value

if TYPE_CHECKING:
    from xstate.action import Action
    from xstate.state_node import StateNode


class State:
    configuration: Set["StateNode"]
    value: str
    context: Dict[str, Any]
    actions: List["Action"]

    def __init__(
        self,
        configuration: Set["StateNode"],
        context: Dict[str, Any],
        actions: List["Action"] = [],
    ):
        root = next(iter(configuration)).machine.root
        self.configuration = configuration
        self.value = get_state_value(root, configuration)
        self.context = context
        self.actions = actions

    def __repr__(self):
        return repr(
            {
                "value": self.value,
                "context": self.context,
                "actions": self.actions,
            }
        )
