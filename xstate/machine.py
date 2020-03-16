from typing import Dict, List
from xstate.state_node import StateNode
from xstate.state import State


class Machine:
    root: StateNode
    _id_map: Dict[str, StateNode]

    def __init__(self, config):
        self.id = config["id"]
        self._id_map = {}
        self.root = StateNode(
            config, machine=self, key=config.get("id", "(machine)"), parent=self
        )
        self.states = self.root.states

    def transition(self, state: State, event: str):
        state_node = self.root.states.get(state.value, None)

        if state_node is None:
            raise ValueError("nope")

        transition = state_node.on.get(event, None)

        if transition is None:
            raise ValueError("transition does not exist")

        return transition.target

    def _register(self, state_node: StateNode):
        state_node.machine = self
        self._id_map[state_node.id] = state_node

    def _get_by_id(self, id: str) -> StateNode:
        return self._id_map.get(id, None)

    def _get_configuration(self, state_value, parent=None) -> List[StateNode]:
        if parent is None:
            parent = self.root

        if isinstance(state_value, str):
            state_node = parent.states.get(state_value, None)

            if state_node is None:
                raise ValueError(f"State node {state_value} is missing")

            return [state_node]

        configuration = []

        for key in state_value.keys():
            state_node = parent.states.get(key)
            configuration.append(state_node)

            configuration += self._get_configuration(
                state_value.get(key), parent=state_node
            )

        return configuration

