from __future__ import annotations
from typing import List, Union, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from xstate.state_node import StateNode


class Transition:
    event: str
    source: StateNode
    target: List[StateNode]
    config: Union[str, StateNode, Any]
    # "internal" or "external"
    type: str

    def __init__(self, config, source: StateNode, event: str):
        self.event = event
        self.config = config
        self.source = source
        self.type = "external"

    @property
    def target(self) -> List[StateNode]:
        if isinstance(self.config, str):
            return [self.source._get_relative(self.config)]
        elif self.config.id:
            return [self.config]
        else:
            return [self.source._get_relative(v) for v in self.config["target"]]
