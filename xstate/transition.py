from __future__ import annotations
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from xstate.state_node import StateNode


class Transition:
    event: str
    source: StateNode
    # "internal" or "external"
    type: str

    def __init__(self, config, source, event: str):
        self.event = event
        self.config = config if not isinstance(config, str) else {"target": [config]}
        self.source = source

    @property
    def target(self) -> List[StateNode]:
        return [self.source._get_relative(v) for v in self.config["target"]]
