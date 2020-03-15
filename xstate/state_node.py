from __future__ import annotations
from typing import Dict, TYPE_CHECKING

from xstate.transition import Transition

if TYPE_CHECKING:
    from xstate.machine import Machine


class StateNode:
    on: Dict[str, Transition]
    machine: Machine
    parent: StateNode

    def __init__(self, config, machine: Machine, key: str, parent: StateNode = None):
        self.parent = parent
        self.id = config.get("id", parent.id + "." + key)

        self.key = key
        self.states = {
            k: StateNode(v, machine=machine, parent=self, key=k)
            for k, v in config.get("states", {}).items()
        }
        self.on = {
            k: Transition(v, source=self, event=k)
            for k, v in config.get("on", {}).items()
        }

        machine._register(self)

    def _get_relative(self, target: str) -> StateNode:
        if target.startswith("#"):
            return self.machine._get_by_id(target[1:])

        return self.parent.states.get(target, None)
