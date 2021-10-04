from __future__ import (
    annotations,
)  #  PEP 563:__future__.annotations will become the default in Python 3.11
from typing import TYPE_CHECKING, Dict, List, Union
import logging

logger = logging.getLogger(__name__)

# from xstate import transition

from xstate.algorithm import (
    enter_states,
    path_to_state_value,
    get_configuration_from_state,
    macrostep,
    main_event_loop,
    get_configuration_from_js,
)

if TYPE_CHECKING:
    from xstate.state import State
    from xstate.state import StateType

from xstate.event import Event
from xstate.state import State
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

    def __init__(self, config: Union[Dict, str], actions={}):
        """[summary]

        Args:
            config ( Union[Dict,str]): A machine configuration either str snippet in Javascript  or dict
            actions (dict, optional): A set of Actions. Defaults to {}.

        Raises:
            Exception: Invalid snippet of Javascript for Machine configuration
        """
        if isinstance(config, str):
            try:
                config = get_configuration_from_js(config)
            except Exception as e:
                raise f"Invalid snippet of Javascript for Machine configuration, Exception:{e}"

        self.id = config.get("id", "(machine)")
        self._id_map = {}
        self.root = StateNode(config, machine=self, parent=None)
        self.states = self.root.states
        self.config = config
        self.actions = actions

    def transition(self, state: StateType, event: str):
        # BUG state could be an `id` of type  `str` representing a state
        # if isinstance(state,str):
        #     state = get_state(state)
        # BUG get_configuration_from_state should handle a str, state_value should be deterimed in the function

        # if (state instanceof State_1.State) {
        if isinstance(state, State):
            #     currentState =
            #         context === undefined
            #             ? state
            #             : this.resolveState(State_1.State.from(state, context));
            # TODO implement context
            # currentState = state if   context is None else  self.resolve_state(State.from(state, context)
            currentState = state
        # else {
        else:
            #     var resolvedStateValue = utils_1.isString(state)
            #         ? this.resolve(utils_1.pathToStateValue(this.getResolvedPath(state)))
            #         : this.resolve(state);
            resolved_state_value = (
                self.root.resolve(
                    path_to_state_value(self.root._get_resolved_path(state))
                )
                if isinstance(state, str)
                else self.resolve(state)
            )

            #     var resolvedContext = context !== null && context !== void 0 ? context : this.machine.context;
            #     currentState = this.resolveState(State_1.State.from(resolvedStateValue, resolvedContext));

            # TODO implement context
            # resolved_context = context  if context is not None and  && context !== void 0 ? : this.machine.context;
            currentState = self.root.resolve_state(
                State._from(
                    state_value=resolved_state_value,
                    # TODO implement context
                    context=None,  # resolvedContext
                )
            )

        configuration = get_configuration_from_state(  # TODO DEBUG FROM HERE
            from_node=self.root, state=currentState, partial_configuration=set()
        )

        possible_transitions = list(configuration)[0].transitions
        (configuration, _actions, transitions) = main_event_loop(
            configuration, Event(event)
        )

        actions, warnings = self._get_actions(_actions)
        for w in warnings:
            logger.warning(w)

        return State(
            configuration=configuration,
            context={},
            actions=actions,
            transitions=transitions,
        )

    def _get_actions(self, actions) -> List[lambda: None]:
        result = []
        errors = []
        for action in actions:
            if action.type in self.actions:
                result.append(self.actions[action.type])
            elif callable(action.type):
                result.append(action.type)
            elif callable(action.exec):
                result.append(action.exec)
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
        (configuration, _actions, internal_queue, transitions) = enter_states(
            enabled_transitions=[self.root.initial_transition],
            configuration=set(),
            states_to_invoke=set(),
            history_value={},
            actions=[],
            internal_queue=[],
            transitions=[],
        )

        (configuration, _actions, transitions) = macrostep(
            configuration=configuration,
            actions=_actions,
            internal_queue=internal_queue,
            transitions=transitions,
        )

        actions, warnings = self._get_actions(_actions)
        for w in warnings:
            print(w)

        return State(
            configuration=configuration,
            context={},
            actions=actions,
            transitions=transitions,
        )
