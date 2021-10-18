from __future__ import annotations
from multiprocessing import (
    Condition,
)  #  PEP 563:__future__.annotations will become the default in Python 3.11
import logging
from typing_extensions import get_args

logger = logging.getLogger(__name__)

from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Set,
    Tuple,
    Union,
    Iterable,
)

# from xstate.state import StateValue  # , StateLike

# from xstate.types import StateLike

# TODO: why does this cause pytest to fail, ImportError: cannot import name 'get_state_value' from 'xstate.algorithm'
# Workaround: supress import and in `get_configuration_from_state` put state: [Dict,str]
# from xstate.state import StateType
from xstate.environment import IS_PRODUCTION, WILDCARD, STATE_IDENTIFIER, NULL_EVENT

from xstate.constants import (
    STATE_DELIMITER,
    TARGETLESS_KEY,
    DEFAULT_GUARD_TYPE,
)

if TYPE_CHECKING:
    from xstate.types import (
        Record,
        Guard,
        DoneEventObject,
        StateLike,
        StateValue,
        Configuration,
        AdjList,
        SCXML,
        # HistoryValue
    )
    from xstate.action import Action
    from xstate.transition import Transition
    from xstate.state_node import StateNode
    from xstate.state import StateType
    from xstate.event import Event


    from xstate.state import State

    # HistoryValue = Dict[str, Set[StateNode]]
from xstate.types import (
        HistoryValue
    )


from xstate.event import Event
from xstate.action_types import ActionTypes


import js2py


def compute_entry_set(
    transitions: List[Transition],
    states_to_enter: Set[StateNode],
    states_for_default_entry: Set[StateNode],
    default_history_content: Dict,
    history_value: HistoryValue,
    current_state: StateValue,
):
    for t in transitions:
        for s in t.target_consider_history(history_value= history_value):
            add_descendent_states_to_enter(
                s,
                states_to_enter=states_to_enter,
                states_for_default_entry=states_for_default_entry,
                default_history_content=default_history_content,
                history_value=history_value,
            )
        ancestor = get_transition_domain(t, history_value=history_value)
        for s in get_effective_target_states(t, history_value=history_value):
            add_ancestor_states_to_enter(
                s,
                ancestor=ancestor,
                states_to_enter=states_to_enter,
                states_for_default_entry=states_for_default_entry,
                default_history_content=default_history_content,
                history_value=history_value,
            )


def add_descendent_states_to_enter(  # noqa C901 too complex. TODO: simplify function
    state: StateNode,
    states_to_enter: Set[StateNode],
    states_for_default_entry: Set[StateNode],
    default_history_content: Dict,
    history_value: HistoryValue,
):
    if is_history_state(state):
        if history_value.states:
            for s in history_value.states[state.parent.key].states:
                add_descendent_states_to_enter(
                    state.parent.get_state_node(s),
                    states_to_enter=states_to_enter,
                    states_for_default_entry=states_for_default_entry,
                    default_history_content=default_history_content,
                    history_value=history_value,
                )
            for s in history_value.states[state.parent.key].states:
                add_ancestor_states_to_enter(
                    state.parent.get_state_node(s),
                    ancestor=state.parent,
                    states_to_enter=states_to_enter,
                    states_for_default_entry=states_for_default_entry,
                    default_history_content=default_history_content,
                    history_value=history_value,
                )
        else:
            # default_history_content[state.parent.id] = state.transition.content
            #TODO: WIP -histoy parallel , following a workaround for implementation to resolve
            default_history_content[state.parent.id] = None
            # for s in state.transition.target:
            #     add_descendent_states_to_enter(
            #         s,
            #         states_to_enter=states_to_enter,
            #         states_for_default_entry=states_for_default_entry,
            #         default_history_content=default_history_content,
            #         history_value=history_value,
            #     )
            # for s in state.transition.target:
            #     add_ancestor_states_to_enter(
            #         s,
            #         ancestor=s.parent,
            #         states_to_enter=states_to_enter,
            #         states_for_default_entry=states_for_default_entry,
            #         default_history_content=default_history_content,
            #         history_value=history_value,
            #     )
    else:
        states_to_enter.add(state)
        if is_compound_state(state):
            states_for_default_entry.add(state)
            for s in state.initial_transition.target:
                add_descendent_states_to_enter(
                    s,
                    states_to_enter=states_to_enter,
                    states_for_default_entry=states_for_default_entry,
                    default_history_content=default_history_content,
                    history_value=history_value,
                )
            for s in state.initial_transition.target:
                add_ancestor_states_to_enter(
                    s,
                    ancestor=s.parent,
                    states_to_enter=states_to_enter,
                    states_for_default_entry=states_for_default_entry,
                    default_history_content=default_history_content,
                    history_value=history_value,
                )
        else:
            if is_parallel_state(state):
                for child in get_child_states(state):
                    if not any([is_descendent(s, child) for s in states_to_enter]):
                        add_descendent_states_to_enter(
                            child,
                            states_to_enter=states_to_enter,
                            states_for_default_entry=states_for_default_entry,
                            default_history_content=default_history_content,
                            history_value=history_value,
                        )


def is_history_state(state: StateNode) -> bool:
    return state.type == "history"


def is_compound_state(state: StateNode) -> bool:
    return state.type == "compound"


def is_atomic_state(state: StateNode) -> bool:
    return any(
        state.type == state_type for state_type in ["atomic", "final", "history"]
    )


def is_descendent(state: StateNode, state2: StateNode) -> bool:
    marker = state

    while marker.parent and marker.parent != state2:
        marker = marker.parent

    return marker.parent == state2


def get_transition_domain(
    transition: Transition, history_value: HistoryValue
) -> StateNode:
    tstates = get_effective_target_states(transition, history_value=history_value)
    if not tstates:
        return None
    elif (
        transition.type == "internal"
        and is_compound_state(transition.source)
        and all([is_descendent(s, state2=transition.source) for s in tstates])
    ):
        return transition.source
    else:
        return find_lcca([transition.source] + list(tstates))


def find_lcca(state_list: List[StateNode]):
    for anc in get_proper_ancestors(state_list[0], state2=None):
        if all([is_descendent(s, state2=anc) for s in state_list[1:]]):
            return anc


def get_effective_target_states(
    transition: Transition, history_value: HistoryValue
) -> Set[StateNode]:
    targets: Set[StateNode] = set()

    for s in transition.target_consider_history(history_value=history_value):
        if is_history_state(s):
            if history_value.get(s.id):
                targets.update(history_value.get(s.id))
            else:
                targets.update(
                    get_effective_target_states(
                        s.transition, history_value=history_value
                    )
                )
        else:
            targets.add(s)

    return targets


def add_ancestor_states_to_enter(
    state: StateNode,
    ancestor: StateNode,
    states_to_enter: Set[StateNode],
    states_for_default_entry: Set[StateNode],
    default_history_content: Dict,
    history_value: HistoryValue,
):
    for anc in get_proper_ancestors(state, state2=ancestor):
        states_to_enter.add(anc)
        if is_parallel_state(anc):
            for child in get_child_states(anc):
                if not any([is_descendent(s, state2=child) for s in states_to_enter]):
                    add_descendent_states_to_enter(
                        child,
                        states_to_enter=states_to_enter,
                        states_for_default_entry=states_for_default_entry,
                        default_history_content=default_history_content,
                        history_value=history_value,
                    )


def get_proper_ancestors(
    state1: StateNode, state2: Optional[StateNode]
) -> List[StateNode]:
    ancestors: List[StateNode] = []
    marker = state1.parent
    while marker and marker != state2:
        ancestors.append(marker)
        marker = marker.parent

    return ancestors


# export function getChildren<TC, TE extends EventObject>(
#   stateNode: StateNode<TC, any, TE>
# ): Array<StateNode<TC, any, TE>> {
#   return keys(stateNode.states).map((key) => stateNode.states[key]);
# }
def get_children(state_node: StateNode) -> List[StateNode]:
    return [state_node.states[key] for key, state in state_node.states.items()]
    # return state_node.states.keys()


# export const isLeafNode = (stateNode: StateNode<any, any, any, any>) =>
#   stateNode.type === 'atomic' || stateNode.type === 'final';
def is_state_id(state_id: str) -> bool:
    return state_id[0] == STATE_IDENTIFIER

def is_leaf_node(state_node: StateNode) -> bool:
    return state_node.type == "atomic" or state_node.type == "final"


def is_final_state(state_node: StateNode) -> bool:
    return state_node.type == "final"


def is_parallel_state(state_node: StateNode) -> bool:
    # should return whether state_node.type is parallel
    if state_node.type == "parallel":
        return True
    else:
        return False


def get_child_states(state_node: StateNode) -> List[StateNode]:
    return [state_node.states.get(key) for key in state_node.states.keys()]


def is_in_final_state(configuration: Set[StateNode],state: StateNode, ) -> bool:
    if is_compound_state(state):
        return any(
            [
                is_final_state(s) and (s in configuration)
                for s in get_child_states(state)
            ]
        )
    elif is_parallel_state(state):
        return all(is_in_final_state(configuration,s) for s in get_child_states(state))
    else:
        return False


# /**
#  * Returns an event that represents that a final state node
#  * has been reached in the parent state node.
#  *
#  * @param id The final state node's parent state node `id`
#  * @param data The data to pass into the event
#  */
# export function done(id: string, data?: any): DoneEventObject {
def done(id: str, data: Any) -> DoneEventObject:
    """Returns an event that represents that a final state node
    has been reached in the parent state node.

    Args:
        id (str): The final state node's parent state node `id`
        data (Any): The data to pass into the event

    Returns:
        DoneEventObject: an event that represents that a final state node
                            has been reached in the parent state node.
    """
    #   const type = `${ActionTypes.DoneState}.${id}`;
    type = f"{ActionTypes.DoneState}.{id}"
    #   const eventObject = {
    #     type,
    #     data
    #   };
    event_object = {"type": type, "data": data}

    # TODO: implement this
    #   eventObject.toString = () => type;

    #   return eventObject as DoneEvent;
    return event_object
    # }


def enter_states(
    enabled_transitions: List[Transition],
    configuration: Set[StateNode],
    states_to_invoke: Set[StateNode],
    history_value: HistoryValue,
    actions: List[Action],
    internal_queue: List[Event],
    transitions: List[Transition],
    current_state:State
) -> Tuple[Set[StateNode], List[Action], List[Event]]:
    states_to_enter: Set[StateNode] = set()
    states_for_default_entry: Set[StateNode] = set()

    default_history_content = {}

    compute_entry_set(
        enabled_transitions,
        states_to_enter=states_to_enter,
        states_for_default_entry=states_for_default_entry,
        default_history_content=default_history_content,
        history_value=history_value,
        current_state=current_state,
    )

    # TODO: sort
    for s in list(states_to_enter):
        configuration.add(s)
        states_to_invoke.add(s)

        # if binding == "late" and s.isFirstEntry:
        #     initializeDataModel(datamodel.s,doc.s)
        #     s.isFirstEntry = false

        # TODO: sort
        for action in s.entry:
            execute_content(action, actions=actions, internal_queue=internal_queue)
        if s in states_for_default_entry:
            # executeContent(s.initial.transition)
            continue
        if default_history_content.get(s.id, None) is not None:
            # executeContent(defaultHistoryContent[s.id])
            continue
        if is_final_state(s):
            parent = s.parent
            grandparent = parent.parent
            internal_queue.append(Event(f"done.state.{parent.id}", s.donedata))
            # transitions.add("TRANSITION") #TODO WIP 21W39

            if grandparent and is_parallel_state(grandparent):
                if all(
                    is_in_final_state( configuration, parent_state)
                    for parent_state in get_child_states(grandparent)
                ):
                    internal_queue.append(Event(f"done.state.{grandparent.id}"))
                    # transitions.add("TRANSITION") #TODO WIP 21W39

        #  const historyValue = currentState
        #   ? currentState.historyValue

        #     ? currentState.historyValue

        #     : stateTransition.source
        #     ? (this.machine.historyValue(currentState.value) as HistoryValue)
        #     : undefined

        #   : undefined;      
        #TODO check statein-tests where  current_state is a dict type
        hv = current_state.history_value if current_state and current_state.history_value else (
                        s.machine.root._history_value(current_state.value if str(type(current_state)) == "<class 'xstate.state.State'>" else None) if list(enabled_transitions)[0].source else (
                            None if s else None))
        if hv:
            history_value.update(hv.__dict__)

    return (configuration, actions, internal_queue, transitions)


def exit_states(
    enabled_transitions: List[Transition],
    configuration: Set[StateNode],
    states_to_invoke: Set[StateNode],
    history_value: HistoryValue,
    actions: List[Action],
    internal_queue: List[Event],
    current_state:State,
):
    states_to_exit = compute_exit_set(
        enabled_transitions, configuration=configuration, history_value=history_value, 
        # current_state=current_state,
    )
    for s in states_to_exit:
        states_to_invoke.discard(s)
    #     statesToExit = statesToExit.toList().sort(exitOrder)
    # for s in states_to_exit:
    #     for h in s.history
    for s in states_to_exit:
        for action in s.exit:
            execute_content(action, actions=actions, internal_queue=internal_queue)
        # for inv in s.invoke:
        #     cancelInvoke(inv)
        configuration.remove(s)

    return (
        configuration,
        actions,
    )


def compute_exit_set(
    enabled_transitions: List[Transition],
    configuration: Set[StateNode],
    history_value: HistoryValue,
) -> Set[StateNode]:
    states_to_exit: Set[StateNode] = set()
    for t in enabled_transitions:
        if t.target_consider_history(history_value=history_value):
            domain = get_transition_domain(t, history_value=history_value)
            for s in configuration:
                if is_descendent(s, state2=domain):
                    states_to_exit.add(s)

    return states_to_exit


def name_match(event: str, specific_event: str) -> bool:
    return event == specific_event


def condition_match(transition: Transition) -> bool:
    return transition.cond() if transition.cond else True


def select_transitions(event: Event, configuration: Set[StateNode]):
    enabled_transitions: Set[Transition] = set()
    atomic_states = [s for s in configuration if is_atomic_state(s)]
    for state_node in atomic_states:
        break_loop = False
        for s in [state_node] + get_proper_ancestors(state_node, None):
            if break_loop:
                break
            for t in sorted(s.transitions, key=lambda t: t.order):
                if t.event and name_match(t.event, event.name) and condition_match(t):
                    enabled_transitions.add(t)
                    break_loop = True

    enabled_transitions = remove_conflicting_transitions(
        enabled_transitions, configuration=configuration, history_value={}  # TODO
    )

    return enabled_transitions


def select_eventless_transitions(configuration: Set[StateNode]):
    enabled_transitions: Set[Transition] = set()
    atomic_states = filter(is_atomic_state, configuration)

    loop = True
    for state in atomic_states:
        if not loop:
            break
        for s in [state] + get_proper_ancestors(state, None):
            for t in sorted(s.transitions, key=lambda t: t.order):
                if not t.event and condition_match(t):
                    enabled_transitions.add(t)
                    loop = False

    enabled_transitions = remove_conflicting_transitions(
        enabled_transitions=enabled_transitions,
        configuration=configuration,
        history_value={},  # TODO
    )
    return enabled_transitions


def remove_conflicting_transitions(
    enabled_transitions: Set[Transition],
    configuration: Set[StateNode],
    history_value: HistoryValue,
):
    enabled_transitions = sorted(enabled_transitions, key=lambda t: t.order)

    filtered_transitions: Set[Transition] = set()
    for t1 in enabled_transitions:
        t1_preempted = False
        transitions_to_remove: Set[Transition] = set()
        for t2 in filtered_transitions:
            t1_exit_set = compute_exit_set(
                enabled_transitions=[t1],
                configuration=configuration,
                history_value=history_value,
            )
            t2_exit_set = compute_exit_set(
                enabled_transitions=[t2],
                configuration=configuration,
                history_value=history_value,
            )
            intersection = [value for value in t1_exit_set if value in t2_exit_set]

            if intersection:
                if is_descendent(t1.source, t2.source):
                    transitions_to_remove.add(t2)
                else:
                    t1_preempted = True
                    break
        if not t1_preempted:
            for t3 in transitions_to_remove:
                filtered_transitions.remove(t3)
            filtered_transitions.add(t1)

    return filtered_transitions


def main_event_loop(
    configuration: Set[StateNode], event: Event,
    current_state:State
) -> Tuple[Set[StateNode], List[Action]]:
    states_to_invoke: Set[StateNode] = set()
    history_value = current_state.history_value if current_state.history_value else HistoryValue()
    transitions = set()
    enabled_transitions = select_transitions(event=event, configuration=configuration)
    transitions = transitions.union(enabled_transitions)
    (configuration, actions, internal_queue, transitions) = microstep(
        enabled_transitions,
        configuration=configuration,
        states_to_invoke=states_to_invoke,
        history_value=history_value,
        transitions=transitions,
        current_state=current_state
    )

    (configuration, actions, transitions) = macrostep(
        configuration=configuration,
        actions=actions,
        internal_queue=internal_queue,
        transitions=transitions,
        current_state=current_state,
    )

    return (configuration, actions, transitions,history_value)


def macrostep(
    configuration: Set[StateNode],
    actions: List[Action],
    internal_queue: List[Event],
    transitions: List[Transition],
    current_state: State=None,
) -> Tuple[Set[StateNode], List[Action]]:
    enabled_transitions = set()
    macrostep_done = False

    while not macrostep_done:
        enabled_transitions = select_eventless_transitions(configuration=configuration)

        if not enabled_transitions:
            if not internal_queue:
                macrostep_done = True
            else:
                internal_event = internal_queue.pop()
                enabled_transitions = select_transitions(
                    event=internal_event,
                    configuration=configuration,
                )
        if enabled_transitions:
            (configuration, actions, internal_queue, transitions) = microstep(
                enabled_transitions=enabled_transitions,
                configuration=configuration,
                states_to_invoke=set(),  # TODO
                history_value={},  # TODO
                transitions=transitions,
                current_state=current_state,
            )

    return (configuration, actions, transitions)


def execute_transition_content(
    enabled_transitions: List[Transition],
    actions: List[Action],
    internal_queue: List[Event],
):
    for transition in enabled_transitions:
        for action in transition.actions:
            execute_content(action, actions, internal_queue)


def execute_content(action: Action, actions: List[Action], internal_queue: List[Event]):
    if action.type == ActionTypes.Raise or action.type == "xstate:raise":
        internal_queue.append(Event(name=action.data.get("event")))
    else:
        actions.append(action)


def microstep(
    enabled_transitions: List[Transition],
    transitions: List[Transition],
    configuration: Set[StateNode],
    states_to_invoke: Set[StateNode],
    history_value: HistoryValue,
    current_state:State,
) -> Tuple[Set[StateNode], List[Action], List[Event]]:
    actions: List[Action] = []
    internal_queue: List[Event] = []

    exit_states(
        enabled_transitions,
        configuration=configuration,
        states_to_invoke=states_to_invoke,
        history_value=history_value,
        actions=actions,
        internal_queue=internal_queue,
        current_state=current_state,
    )

    execute_transition_content(
        enabled_transitions, actions=actions, internal_queue=internal_queue
    )

    enter_states(
        enabled_transitions,
        configuration=configuration,
        states_to_invoke=states_to_invoke,
        history_value=history_value,
        actions=actions,
        internal_queue=internal_queue,
        transitions=transitions,
        current_state=current_state,
    )

    return (configuration, actions, internal_queue, transitions)


def is_machine(value):
    try:
        return "__xstatenode" in value
    except:
        return False


# export function toGuard<TContext, TEvent extends EventObject>(
#   condition?: Condition<TContext, TEvent>,
#   guardMap?: Record<string, ConditionPredicate<TContext, TEvent>>
# ): Guard<TContext, TEvent> | undefined {


def to_guard(condition: Condition, guardMap: Record) -> Guard:
    #   if (!condition) {
    #     return undefined;
    #   }
    if condition == None:
        return None

    #   if (isString(condition)) {
    #     return {
    #       type : DEFAULT_GUARD_TYPE,
    #       name: condition,
    #       predicate: guardMap ? guardMap[condition] : undefined
    #     };
    #   }

    if isinstance(condition, str):
        return {
            "type": DEFAULT_GUARD_TYPE,
            "name": condition,
            "predicate": guardMap[condition] if guardMap else None,
        }

    #   if (isFunction(condition)) {
    #     return {
    #       type : DEFAULT_GUARD_TYPE,
    #       name: condition.name,
    #       predicate: condition
    #     };
    #   }

    if callable(condition):
        return {
            "type": DEFAULT_GUARD_TYPE,
            "name": condition["name"],
            "predicate": condition,
        }

    #   return condition;
    return condition


def to_array_strict(value: Any) -> List:
    if isinstance(value, List):
        return value
    return [value]


# export function toArray<T>(value: T[] | T | undefined): T[] {
#   if (value === undefined) {
#     return [];
#   }
#   return toArrayStrict(value);
# }
def to_array(value: Union[str, List, None]) -> List:
    if not value:
        return []

    return to_array_strict(value)


# ===================
def to_transition_config_array(event, configLike) -> List:
    transitions = {
        {"target": transition_like, "event": event}
        for transition_like in to_array_strict(configLike)
        if (
            #   isinstance(transition_like,'undefined') or
            isinstance(transition_like, str)
            or is_machine(transition_like)
        )
    }
    return transitions


# export function normalizeTarget<TContext, TEvent extends EventObject>(
#   target: SingleOrArray<string | StateNode<TContext, any, TEvent>> | undefined
# ): Array<string | StateNode<TContext, any, TEvent>> | undefined {
#   if (target === undefined || target === TARGETLESS_KEY) {
#     return undefined;
#   }
#   return toArray(target);
# }


def normalize_target(
    target: Union[List[str], StateNode]
) -> Union[List[str], StateNode]:

    if not target or target == TARGETLESS_KEY:
        return None

    return to_array(target)


def flatten(t: List) -> List:
    return [item for sublist in t for item in sublist]


def get_configuration(
    prev_state_nodes: Iterable[StateNode], state_nodes: Iterable[StateNode]
) -> Iterable[StateNode]:

    # export function getConfiguration<TC, TE extends EventObject>(
    #   prevStateNodes: Iterable<StateNode<TC, any, TE, any>>,
    #   stateNodes: Iterable<StateNode<TC, any, TE, any>>
    # ): Iterable<StateNode<TC, any, TE, any>> {

    #   const prevConfiguration = new Set(prevStateNodes);
    #   const prevAdjList = getAdjList(prevConfiguration);
    prev_configuration = set(prev_state_nodes)
    prev_adj_list = get_adj_list(prev_configuration)

    configuration = set(state_nodes)

    #   // add all ancestors
    #   for (const s of configuration) {
    #     let m = s.parent;

    #     while (m && !configuration.has(m)) {
    #       configuration.add(m);
    #       m = m.parent;
    #     }
    #   }

    # for s in configuration:
    current_configuration = configuration.copy()
    for s in current_configuration:
        m = s.parent
        while m and m not in current_configuration:
            configuration.add(m)
            m = m.parent

    #   const adjList = getAdjList(configuration);
    adjList = get_adj_list(configuration)

    #   // add descendants
    #   for (const s of configuration) {
    current_configuration = configuration.copy()
    for s in current_configuration:

        #     // if previously active, add existing child nodes
        #     if (s.type === 'compound' && (!adjList.get(s) || !adjList.get(s)!.length)) {
        if s.type == "compound" and (s.id not in adjList or len(adjList[s.id]) == 0):

            #       if (prevAdjList.get(s)) {
            if prev_adj_list.get(s.id, None):
                #         prevAdjList.get(s)!.forEach((sn) => configuration.add(sn));
                [configuration.add(sn) for sn in prev_adj_list.get(s.id, None)]
            #       } else {
            else:
                #         s.initialStateNodes.forEach((sn) => configuration.add(sn));
                [configuration.add(sn) for sn in s.initial_state_nodes]
        #       }
        #     } else {
        else:
            #       if (s.type === 'parallel') {
            if s.type == "parallel":
                #         for (const child of getChildren(s)) {
                for child in get_children(s):
                    #           if (child.type === 'history') {
                    if child.type == "history":
                        #             continue;
                        continue
                    #           }

                    #           if (!configuration.has(child)) {
                    if child not in current_configuration:
                        #             configuration.add(child);
                        configuration.add(child)

                        #             if (prevAdjList.get(child)) {
                        if child in prev_adj_list:
                            #               prevAdjList.get(child)!.forEach((sn) => configuration.add(sn));
                            [configuration.add(sn) for sn in prev_adj_list[child]]
                        #             } else {
                        else:
                            #               child.initialStateNodes.forEach((sn) => configuration.add(sn));
                            [configuration.add(sn) for sn in child.initial_state_nodes]
        #             }
        #           }
        #         }
        #       }
        #     }
        #   }

    #   // add all ancestors
    #   for (const s of configuration) {
    current_configuration = configuration
    for s in current_configuration:

        #     let m = s.parent;
        m = s.parent

        #     while (m && !configuration.has(m)) {
        #       configuration.add(m);
        #       m = m.parent;
        while m and m not in current_configuration:
            configuration.add(m)
            m = m.parent

    #     }
    #   }

    #   return configuration;
    return configuration


# }


def is_possible_js_config_snippet(config: str):
    return (
        isinstance(config, str)
        and config.lstrip()[0] == "{"
        and config.rstrip()[-1] == "}"
    )


def get_configuration_from_js(config: str) -> dict:
    """Translates a JS config to a xstate_python configuration dict
    config: str  a valid javascript snippet of an xstate machine
    Example
        get_configuration_from_js(
            config=
            ```
              {
                a: 'a2',
                b: {
                  b2: {
                    foo: 'foo2',
                    bar: 'bar1'
                  }
                }
              }
            ```)
        )
    """
    # return js2py.eval_js(f"config = {config.replace(chr(10),'').replace(' ','')}").to_dict()
    return js2py.eval_js(f"config = {config.replace(chr(10),'')}").to_dict()


def get_configuration_from_state(
    from_node: StateNode,
    state: Union[State, Dict, str],
    partial_configuration: Set[StateNode],
) -> Set[StateNode]:
    # TODO TD: isinstance(state,State) requires import which generates circular dependencie issues
    if str(type(state)) == "<class 'xstate.state.State'>":
        state_value = state.value
    else:
        state_value = state
    if isinstance(state_value, str):
        partial_configuration.add(from_node.states.get(state_value))
    else:
        for key in state_value.keys():
            node = from_node.states.get(key)
            partial_configuration.add(node)
            get_configuration_from_state(
                node, state_value.get(key), partial_configuration
            )

    return partial_configuration


# TODO REMOVE an try and resolving some test cases
def DEV_get_configuration_from_state(
    from_node: StateNode,
    state: Union[Dict, str],
    # state: Union[Dict, StateType],
    partial_configuration: Set[StateNode],
) -> Set[StateNode]:
    if isinstance(state, str):
        state = from_node.states.get(state)
        partial_configuration.add(state)
    elif isinstance(state, dict):
        for key in state.keys():
            node = from_node.states.get(key)
            partial_configuration.add(node)
            get_configuration_from_state(node, state.get(key), partial_configuration)
    elif str(type(state)) == "<class 'xstate.state.State'>":
        for state_node in state.configuration:
            node = from_node.states.get(state_node.key)
            partial_configuration.add(node)
            get_configuration_from_state(node, state_node, partial_configuration)
    elif str(type(state)) == "<class 'xstate.state_node.StateNode'>":
        for key in state.config.keys():
            node = from_node.states.get(key)
            partial_configuration.add(node)
            get_configuration_from_state(
                node, state.config.get(key), partial_configuration
            )

    return partial_configuration


def get_adj_list(configuration: Set[StateNode]) -> Dict[str, Set[StateNode]]:
    adj_list: Dict[str, Set[StateNode]] = {}

    for s in configuration:
        if not adj_list.get(s.id):
            adj_list[s.id] = set()

        if s.parent:
            if not adj_list.get(s.parent.id):
                adj_list[s.parent.id] = set()

            adj_list.get(s.parent.id).add(s)

    return adj_list


def get_state_value(state_node: StateNode, configuration: Set[StateNode]):
    return get_value_from_adj(state_node, get_adj_list(configuration))


def path_to_state_value(state_path: List[str]) -> StateValue:
    # export function pathToStateValue(statePath: string[]): StateValue {
    #   if (statePath.length === 1) {
    #     return statePath[0];
    #   }
    if len(state_path) == 1:
        return state_path[0]

    #   const value = {};
    #   let marker = value;
    value = {}
    marker = value

    #   for (let i = 0; i < statePath.length - 1; i++) {
    for i, element in enumerate(state_path[:-1]):
        #     if (i === statePath.length - 2) {
        if i == len(state_path) - 2:
            #       marker[statePath[i]] = statePath[i + 1];
            marker[element] = state_path[i + 1]
        #     } else {
        else:
            #       marker[statePath[i]] = {};
            marker[element] = {}
            #       marker = marker[statePath[i]];
            marker = marker[element]
    return value


def to_state_value(
    state_value: Union[StateLike, StateValue, str],
    # state_value: Union[StateValue, str],
    delimiter,
) -> StateValue:
    # export function toStateValue(
    #   stateValue: StateLike<any> | StateValue | string[],
    #   delimiter: string
    # ): StateValue {

    #   if (isStateLike(stateValue)) {
    #     return stateValue.value;
    #   }
    if is_state_like(state_value):
        return state_value.value
    #   if (isArray(stateValue)) {
    #     return pathToStateValue(stateValue);
    #   }
    if isinstance(state_value, List):
        return path_to_state_value(to_state_value)

    # if (typeof stateValue !== 'string') {
    #     return stateValue;
    # }
    if not isinstance(state_value, str):
        return state_value

    # for a js config snippet
    if isinstance(state_value, str):
        # TODO: do we really have to process js snippets
        if is_possible_js_config_snippet(state_value):
            # state_value = repr(get_configuration_from_js(state_value))
            state_value = get_configuration_from_js(state_value)
            return state_value
        else:
            #   const statePath = toStatePath(stateValue as string, delimiter);
            state_path = to_state_path(state_value, delimiter)
            #   return pathToStateValue(statePath);
            return path_to_state_value(state_path)
    # }


def to_state_path(state_id: str, delimiter: str = ".") -> List[str]:
    try:
        if isinstance(state_id, List):
            return state_id

        return state_id.split(delimiter)
    except Exception as e:
        raise Exception(f"{state_id} is not a valid state path")


# export function toStatePaths(stateValue: StateValue | undefined): string[][] {
def to_state_paths(state_value: Union[StateValue, None]) -> List[str]:

    #   if (!stateValue) {
    #     return [[]];
    #   }
    if state_value is None:
        return [[]]

    #   if (isString(stateValue)) {
    #     return [[stateValue]];
    #   }
    if isinstance(state_value, str):
        return [[state_value]]

    #   const result = flatten(
    #     keys(stateValue).map((key) => {
    #       const subStateValue = stateValue[key];

    def map_function(key):
        #   const subStateValue = stateValue[key];
        sub_state_value = state_value[key]
        #       if (
        #         typeof subStateValue !== 'string' &&
        #         (!subStateValue || !Object.keys(subStateValue).length)
        #       ) {
        #         return [[key]];
        #       }
        if not isinstance(sub_state_value, str) and (
            sub_state_value is  None or not len(sub_state_value) > 0
        ):
            return [[key]]

        #       return toStatePaths(stateValue[key]).map((subPath) => {
        #         return [key].concat(subPath);
        #       });
        return [[key]+sub_path for sub_path in to_state_paths(state_value[key])]
        #     })
        #   );

    result = flatten([map_function(key) for key in state_value.keys()])

    #   return result;
    return result
    # return flatten(result)
    # }


# export function toEventObject<TEvent extends EventObject>(
#   event: Event<TEvent>,
#   payload?: EventData
#   // id?: TEvent['type']
# ): TEvent {
def to_event_object(
     event: Event,
    **kwargs
)->Event:

#   if (isString(event) || typeof event === 'number') {
#     return { type: event, ...payload } as TEvent;
#   }

    if isinstance(event,str) or isinstance(event, int ):
        return { "type": event, **kwargs}
#   }

#   return event;
    return event
# }

# export function toSCXMLEvent<TEvent extends EventObject>(
#   event: Event<TEvent> | SCXML.Event<TEvent>,
#   scxmlEvent?: Partial<SCXML.Event<TEvent>>
# ): SCXML.Event<TEvent> {
def to_scxml_event(
  event: Event,
)->SCXML.Event:

#   if (!isString(event) && '$$type' in event && event.$$type === 'scxml') {
#     return event as SCXML.Event<TEvent>;
#   }
  if not isinstance(event,str) and '__type' in event and event.__type == 'scxml':
    return event
  

#   const eventObject = toEventObject(event as Event<TEvent>);
  event_object = to_event_object(event)

#   return {
#     name: eventObject.type,
#     data: eventObject,
#     $$type: 'scxml',
#     type: 'external',
#     ...scxmlEvent
#   };
  return {
    "name": event_object['type'].value[0],
    "data": event_object,
    "__type": 'scxml',
    "_type": 'external',
    # ...scxmlEvent
  }

# }

def is_state_like(state: any) -> bool:
    return (
        isinstance(state, object)
        # TODO: which objects are state like ?
        and "<class 'xstate" in str(type(state))
        and "value" in vars(state)
        and "context" in vars(state)
        # TODO : Eventing to be enabled sometime
        # and 'event' in vars(state)
        # and '_event' in vars(state)
    )


# export function toStateValue(
#   stateValue: StateLike<any> | StateValue | string[],
#   delimiter: string
# ): StateValue {
#   if (isStateLike(stateValue)) {
#     return stateValue.value;
#   }

#   if (isArray(stateValue)) {
#     return pathToStateValue(stateValue);
#   }

#   if (typeof stateValue !== 'string') {
#     return stateValue as StateValue;
#   }

#   const statePath = toStatePath(stateValue as string, delimiter);

#   return pathToStateValue(statePath);
# }

# export function pathToStateValue(statePath: string[]): StateValue {
#   if (statePath.length === 1) {
#     return statePath[0];
#   }

#   const value = {};
#   let marker = value;

#   for (let i = 0; i < statePath.length - 1; i++) {
#     if (i === statePath.length - 2) {
#       marker[statePath[i]] = statePath[i + 1];
#     } else {
#       marker[statePath[i]] = {};
#       marker = marker[statePath[i]];
#     }
#   }

#   return value;
# }


def get_value_from_adj(state_node: StateNode, adj_list: Dict[str, Set[StateNode]]):
    child_state_nodes = adj_list.get(state_node.id)

    if is_compound_state(state_node):
        child_state_node = list(child_state_nodes)[0] if child_state_nodes != set() else None

        if child_state_node:
            if is_atomic_state(child_state_node):
                return child_state_node.key
        else:
            return {}

    state_value = {}

    for s in child_state_nodes:
        state_value[s.key] = get_value_from_adj(s, adj_list)

    return state_value


# export function getValue<TC, TE extends EventObject>(
#   rootNode: StateNode<TC, any, TE, any>,
#   configuration: Configuration<TC, TE>
# ): StateValue {
#   const config = getConfiguration([rootNode], configuration);

#   return getValueFromAdj(rootNode, getAdjList(config));
# }

def get_value(
  root_node: StateNode,
  configuration: Configuration
)->StateValue:
  config = get_configuration([root_node], configuration)

  return get_value_from_adj(root_node, get_adj_list(config))



def map_values(collection: Dict[str, Any], iteratee: Callable):
    result = {}
    collection_keys = collection.keys()

    for i, key in enumerate(collection_keys):
        args = (collection[key], key, collection, i)
        result[key] = iteratee(*args)

    return result


# export function mapFilterValues<T, P>(
#   collection: { [key: string]: T },
#   iteratee: (item: T, key: string, collection: { [key: string]: T }) => P,
#   predicate: (item: T) => boolean
# ): { [key: string]: P } {

def map_filter_values(
  collection: Dict ,
  #TODO: define valid types
  iteratee: Any,  #(item: T, key: string, collection: { [key: string]: T }) => P,
  predicate: Any #(item: T) => boolean
)-> Dict:

    #   const result: { [key: string]: P } = {};
    result = {} 

    #   for (const key of keys(collection)) {
    for key,item in collection.items():

    #     const item = collection[key];
        pass

    #     if (!predicate(item)) {
    #       continue;
    #     }
        if not predicate(item):
            continue

    #     result[key] = iteratee(item, key, collection);
        result[key] = iteratee(item, key, collection);

    #   return result;
    return result


# /**
#  * Retrieves a value at the given path via the nested accessor prop.
#  * @param props The deep path to the prop of the desired value
#  */
# export function nestedPath<T extends Record<string, any>>(
#   props: string[],
#   accessorProp: keyof T
# ): (object: T) => T {
def nested_path(
  props: List[str],
  accessorProp: str
)-> Callable: 
#   return (object) => {
#     let result: T = object;
    def func_nested_path(object):
        result =object
        
        for prop in props:
            result = result[accessorProp].get(prop, None) if result[accessorProp] else None
        

        return  result
    return func_nested_path

#     for (const prop of props) {
#       result = result[accessorProp][prop];
#     }

#     return result;
#   };
# }

# /**
#  * Retrieves a value at the given path via the nested accessor prop.
#  * @param props The deep path to the prop of the desired value
#  */
# export function nestedPath<T extends Record<string, any>>(
#   props: string[],
#   accessorProp: keyof T
# ): (object: T) => T {
#   return (object) => {
#     let result: T = object;

#     for (const prop of props) {
#       result = result[accessorProp][prop];
#     }

#     return result;
#   };
# }


# export function updateHistoryStates(
#   hist: HistoryValue,
#   stateValue: StateValue
# ): Record<string, HistoryValue | undefined> {
#   return mapValues(hist.states, (subHist, key) => {
#     if (!subHist) {
#       return undefined;
#     }
#     const subStateValue =
#       (isString(stateValue) ? undefined : stateValue[key]) ||
#       (subHist ? subHist.current : undefined);

#     if (!subStateValue) {
#       return undefined;
#     }

#     return {
#       current: subStateValue,
#       states: updateHistoryStates(subHist, subStateValue)
#     };
#   });
# }


def update_history_states(hist:HistoryValue, state_value)->Dict:
    def lambda_function(*args):
        sub_hist, key = args[0:2]
        if not sub_hist:
            return None

        sub_state_value = ( 
            (None if isinstance(state_value, str) else (state_value.get(key,None) ))
              or (sub_hist.current if sub_hist else None)
              )
        

        if not sub_state_value:
            return None

        return sub_hist.update( {
            "current": sub_state_value,
            "states": update_history_states(sub_hist, sub_state_value),
        })

    return map_values(hist.states, lambda_function)

# export function updateHistoryValue(
#   hist: HistoryValue,
#   stateValue: StateValue
# ): HistoryValue {
#   return {
#     current: stateValue,
#     states: updateHistoryStates(hist, stateValue)
#   };
# }

def update_history_value(hist, state_value):
    return hist.update({
        "current": state_value, 
        "states": update_history_states(hist, state_value)})
