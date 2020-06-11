from __future__ import annotations
from typing import List, Union, Any, TYPE_CHECKING
from xstate.action import Action

if TYPE_CHECKING:
    from xstate.state_node import StateNode


class Transition:
    event: str
    source: StateNode
    config: Union[str, StateNode, Any]
    actions: List[Action]
    # "internal" or "external"
    type: str

    def __init__(self, config, source: StateNode, event: str):
        self.event = event
        self.config = config
        self.source = source
        self.type = "external"

        self.actions = (
            (
                [
                    Action(type=action.get("type"), data=action)
                    for action in config.get("actions", [])
                ]
            )
            if isinstance(config, dict)
            else []
        )

    @property
    def target(self) -> List[StateNode]:
        if isinstance(self.config, str):
            return [self.source._get_relative(self.config)]
        elif isinstance(self.config, dict):
            return [self.source._get_relative(v) for v in self.config["target"]]
        else:
            return [self.config]
