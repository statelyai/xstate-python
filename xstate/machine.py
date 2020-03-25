from typing import Dict, List
from xstate.state_node import StateNode
from xstate.state import State
from xstate.algorithm import enter_states, get_state_value, main_event_loop
from xstate.event import Event


class Machine:
    root: StateNode
    _id_map: Dict[str, StateNode]

    def __init__(self, config):
        self.id = config["id"]
        self._id_map = {}
        self.root = StateNode(
            config, machine=self, key=config.get("id", "(machine)"), parent=None
        )
        self.states = self.root.states

    def transition(self, state: State, event: str):
        (configuration, actions) = main_event_loop(self, state, Event(event))

        value = get_state_value(self.root, configuration=configuration)

        return State(value, context={}, actions=actions)

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

    @property
    def initial_state(self) -> State:
        (configuration, actions) = enter_states(
            [self.root.initial],
            configuration=set(),
            states_to_invoke=set(),
            history_value={},
            actions=[],
        )

        return State(get_state_value(self.root, configuration), {}, actions=actions)
