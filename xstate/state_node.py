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
    parent: Optional[StateNode]
    initial: Optional[Transition]
    entry: List[Action]
    exit: List[Action]
    donedata: Optional[Dict]
    type: str  # 'atomic' or 'compound' or 'parallel' or 'final'
    transitions: List[Transition]
    id: str
    key: str
    states: Dict[str, StateNode]

    def __init__(
        self,
        # { "type": "compound", "states": { ... } }
        config,
        machine: Machine,
        key: str,
        parent: Union[StateNode, Machine] = None,
    ):
        self.parent = parent
        self.id = (
            config.get("id", parent.id + "." + key)
            if parent
            else config.get("id", machine.id + "." + key)
        )
        self.entry = (
            [Action(entry_action.get("type")) for entry_action in config.get("entry")]
            if config.get("entry")
            else []
        )

        self.exit = (
            [Action(exit_action.get("type")) for exit_action in config.get("exit")]
            if config.get("exit")
            else []
        )

        self.key = key
        self.states = {
            k: StateNode(v, machine=machine, parent=self, key=k)
            for k, v in config.get("states", {}).items()
        }
        self.on = {}
        self.transitions = []
        for k, v in config.get("on", {}).items():
            transition = Transition(v, source=self, event=k)
            self.on[k] = transition
            self.transitions.append(transition)

        initial_key = config.get("initial")

        if not initial_key:
            self.initial = None
        else:
            self.initial = Transition(
                self.states.get(initial_key), source=self, event=None
            )

        self.type = config.get("type")

        if self.type is None:
            self.type = "atomic" if not self.states else "compound"

        if self.type == "final":
            self.donedata = config.get("data")

        if config.get("onDone"):
            done_event = f"done.state.{self.id}"
            done_transition = Transition(
                config.get("onDone"), source=self, event=done_event
            )
            self.on[done_event] = done_transition
            self.transitions.append(done_transition)

        machine._register(self)

    def _get_relative(self, target: str) -> StateNode:
        if target.startswith("#"):
            return self.machine._get_by_id(target[1:])

        state_node = self.parent.states.get(target)

        if not state_node:
            raise ValueError(
                f"Relative state node '{target}' does not exist on state node '#{self.id}'"
            )

        return state_node
