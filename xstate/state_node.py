from __future__ import annotations
from typing import Dict, TYPE_CHECKING, Optional, Union, List
from enum import Enum

from xstate.transition import Transition
from xstate.action import Action

if TYPE_CHECKING:
    from xstate.machine import Machine

class StateNode:
    on: Dict[str, Transition]
    machine: Machine
    parent: Union[StateNode, Machine]
    initial: Optional[Transition]
    entry: List[Action]
    exit: List[Action]
    donedata: Optional[Dict]
    type: str # 'atomic' or 'compound' or 'parallel' or 'final'

    def __init__(
        self,
        # { "type": "compound", "states": { ... } }
        config,
        machine: Machine,
        key: str,
        parent: Union[StateNode, Machine] = None,
    ):
        self.parent = parent
        self.id = config.get("id", parent.id + "." + key)
        self.entry = []
        self.exit = []

        self.key = key
        self.states = {
            k: StateNode(v, machine=machine, parent=self, key=k)
            for k, v in config.get("states", {}).items()
        }
        self.on = {
            k: Transition(v, source=self, event=k)
            for k, v in config.get("on", {}).items()
        }
        self.initial = (
            None
            if config.get("initial", None) is None
            else Transition(config.get("initial"), source=self, event=None)
        )

        self.type = config.get('type')

        if self.type is None:
            self.type = 'atomic' if not self.states else 'compound'

        machine._register(self)

    def _get_relative(self, target: str) -> StateNode:
        if target.startswith("#"):
            return self.machine._get_by_id(target[1:])

        return self.parent.states.get(target, None)
