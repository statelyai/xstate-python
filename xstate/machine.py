from typing import Dict
from xstate.state_node import StateNode
from xstate.state import State


class Machine:
    states: Dict[str, StateNode]

    def __init__(self, config):
        self.id = config["id"]
        self._id_map = {}
        self.states = {
            k: StateNode(v, parent=self, machine=self)
            for k, v in config.get("states", {}).items()
        }

    def transition(self, state: State, event: str):
        state_node = self.states.get(state.value, None)

        if state_node is None:
            raise ValueError("nope")

        transition = state_node.on.get(event, None)

        if transition is None:
            raise ValueError("transition does not exist")

        return transition.target
