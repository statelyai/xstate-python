from typing import Dict, List, Union

from xstate.algorithm import (
    enter_states,
    get_configuration_from_state,
    macrostep,
    main_event_loop,
    # get_configuration_from_js
)
# TODO: Work around for import error, don't know why lint unresolved, if import from xstate.algorthim we get import error in `transitions.py`
# Explain : ImportError: cannot import name 'get_configuration_from_js' from 'xstate.algorithm' 
from xstate.utils import (
    get_configuration_from_js
)


from xstate.event import Event
from xstate.state import State, StateType
from xstate.state_node import StateNode


class Machine:
    """[summary]

    Raises:
        f: [description]
        ValueError: [description]

    Returns:
        [type]: [description]
    """
    id: str
    root: StateNode
    _id_map: Dict[str, StateNode]
    config: object
    states: Dict[str, StateNode]
    actions: List[lambda: None]

    def __init__(self, config: Union[Dict,str], actions={}):
        """[summary]

        Args:
            config ( Union[Dict,str]): A machine configuration either str snippet in Javascript  or dict
            actions (dict, optional): A set of Actions. Defaults to {}.

        Raises:
            Exception: Invalid snippet of Javascript for Machine configuration
        """
        if isinstance(config,str):
            try:
                config = get_configuration_from_js(config)
            except Exception as e:
                raise f"Invalid snippet of Javascript for Machine configuration, Exception:{e}"
        
        self.id = config.get("id", "(machine)")
        self._id_map = {}
        self.root = StateNode(
            config, machine=self, key=self.id, parent=None
        )
        self.states = self.root.states
        self.config = config
        self.actions = actions

    def transition(self, state: StateType, event: str):
        # BUG state could be an `id` of type  `str` representing 
        if isinstance(state,str):
            state = get_state(state)
        configuration = get_configuration_from_state( #TODO DEBUG FROM HERE
            from_node=self.root, state_value=state.value, partial_configuration=set()
        )
        (configuration, _actions) = main_event_loop(configuration, Event(event))

        actions, warnings = self._get_actions(_actions)
        for w in warnings:
            print(w)

        return State(configuration=configuration, context={}, actions=actions)

    def _get_actions(self, actions) -> List[lambda: None]:
        result = []
        errors = []
        for action in actions:
            if action.type in self.actions:
                result.append(self.actions[action.type])
            elif callable(action.type):
                result.append(action.type)
            else:
                errors.append("No '{}' action".format(action.type))
        return result, errors

    def state_from(self, state_value) -> State:
        configuration = self._get_configuration(state_value=state_value)

        return State(configuration=configuration, context=None)

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
        (configuration, _actions, internal_queue) = enter_states(
            [self.root.initial],
            configuration=set(),
            states_to_invoke=set(),
            history_value={},
            actions=[],
            internal_queue=[],
        )

        (configuration, _actions) = macrostep(
            configuration=configuration, actions=_actions, internal_queue=internal_queue
        )

        actions, warnings = self._get_actions(_actions)
        for w in warnings:
            print(w)

        return State(configuration=configuration, context={}, actions=actions)
