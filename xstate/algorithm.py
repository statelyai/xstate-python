from __future__ import annotations
from typing import List, Set, Dict, Optional, Tuple, Union, TYPE_CHECKING
from xstate.transition import Transition
from xstate.state_node import StateNode
from xstate.action import Action
from xstate.event import Event

HistoryValue = Dict[str, Set[StateNode]]


def compute_entry_set(
    transitions: List[Transition],
    states_to_enter: Set[StateNode],
    states_for_default_entry: Set[StateNode],
    default_history_content: Dict,
    history_value: HistoryValue,
):
    for t in transitions:
        for s in t.target:
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


def add_descendent_states_to_enter(
    state: StateNode,
    states_to_enter: Set[StateNode],
    states_for_default_entry: Set[StateNode],
    default_history_content: Dict,
    history_value: HistoryValue,
):
    if is_history_state(state):
        if history_value.get(state.id):
            for s in history_value.get(state.id):
                add_descendent_states_to_enter(
                    s,
                    states_to_enter=states_to_enter,
                    states_for_default_entry=states_for_default_entry,
                    default_history_content=default_history_content,
                    history_value=history_value,
                )
            for s in history_value.get(state.id):
                add_ancestor_states_to_enter(
                    s,
                    ancestor=s.parent,
                    states_to_enter=states_to_enter,
                    states_for_default_entry=states_for_default_entry,
                    default_history_content=default_history_content,
                    history_value=history_value,
                )
        else:
            default_history_content[state.parent.id] = state.transition.content
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
            for s in state.initial.target:
                add_descendent_states_to_enter(
                    s,
                    states_to_enter=states_to_enter,
                    states_for_default_entry=states_for_default_entry,
                    default_history_content=default_history_content,
                    history_value=history_value,
                )
            for s in state.initial.target:
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


# function getTransitionDomain(t)
#     tstates = getEffectiveTargetStates(t)
#     if not tstates:
#         return null
#     elif t.type == "internal" and isCompoundState(t.source) and tstates.every(lambda s: isDescendant(s,t.source)):
#         return t.source
#     else:
#         return findLCCA([t.source].append(tstates))
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

    for s in transition.target:
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


# procedure addAncestorStatesToEnter(state, ancestor, statesToEnter, statesForDefaultEntry, defaultHistoryContent)
#     for anc in getProperAncestors(state,ancestor):
#         statesToEnter.add(anc)
#         if isParallelState(anc):
#             for child in getChildStates(anc):
#                 if not statesToEnter.some(lambda s: isDescendant(s,child)):
#                     addDescendantStatesToEnter(child,statesToEnter,statesForDefaultEntry, defaultHistoryContent)
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


def is_in_final_state(state: StateNode, configuration: Set[StateNode]) -> bool:
    if is_compound_state(state):
        return any(
            [
                is_final_state(s) and (s in configuration)
                for s in get_child_states(state)
            ]
        )
    elif is_parallel_state(state):
        return all(is_in_final_state(s, configuration) for s in get_child_states(state))
    else:
        return False


def enter_states(
    enabled_transitions: List[Transition],
    configuration: Set[StateNode],
    states_to_invoke: Set[StateNode],
    history_value: HistoryValue,
    actions: List[Action],
    internal_queue: List[Event],
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

            if is_parallel_state(grandparent):
                if all(
                    is_in_final_state(parent_state, configuration)
                    for parent_state in get_child_states(grandparent)
                ):
                    internal_queue.append(Event(f"done.state.{grandparent.id}"))

    return (configuration, actions, internal_queue)


def exit_states(
    enabled_transitions: List[Transition],
    configuration: Set[StateNode],
    states_to_invoke: Set[StateNode],
    history_value: HistoryValue,
    actions: List[Action],
    internal_queue: List[Event],
):
    states_to_exit = compute_exit_set(
        enabled_transitions, configuration=configuration, history_value=history_value
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
        if t.target:
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
    configuration: Set[StateNode], event: Event
) -> Tuple[Set[StateNode], List[Action]]:
    states_to_invoke: Set[StateNode] = set()
    history_value = {}
    enabled_transitions = select_transitions(event=event, configuration=configuration)

    (configuration, actions, internal_queue) = microstep(
        enabled_transitions,
        configuration=configuration,
        states_to_invoke=states_to_invoke,
        history_value=history_value,
    )

    (configuration, actions) = macrostep(
        configuration=configuration, actions=actions, internal_queue=internal_queue
    )

    return (configuration, actions)


def macrostep(
    configuration: Set[StateNode], actions: List[Action], internal_queue: List[Event]
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
            (configuration, actions, internal_queue) = microstep(
                enabled_transitions=enabled_transitions,
                configuration=configuration,
                states_to_invoke=set(),  # TODO
                history_value={},  # TODO
            )

    return (configuration, actions)


def execute_transition_content(
    enabled_transitions: List[Transition],
    actions: List[Action],
    internal_queue: List[Event],
):
    for transition in enabled_transitions:
        for action in transition.actions:
            execute_content(action, actions, internal_queue)


def execute_content(action: Action, actions: List[Action], internal_queue: List[Event]):
    if action.type == "xstate:raise":
        internal_queue.append(Event(action.data.get("event")))
    else:
        actions.append(action)


def microstep(
    enabled_transitions: List[Transition],
    configuration: Set[StateNode],
    states_to_invoke: Set[StateNode],
    history_value: HistoryValue,
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
    )

    return (configuration, actions, internal_queue)


# ===================


def get_configuration_from_state(
    from_node: StateNode,
    state_value: Union[Dict, str],
    partial_configuration: Set[StateNode],
) -> Set[StateNode]:
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


def get_value_from_adj(state_node: StateNode, adj_list: Dict[str, Set[StateNode]]):
    child_state_nodes = adj_list.get(state_node.id)

    if is_compound_state(state_node):
        child_state_node = list(child_state_nodes)[0]

        if child_state_node:
            if is_atomic_state(child_state_node):
                return child_state_node.key
        else:
            return {}

    state_value = {}

    for s in child_state_nodes:
        state_value[s.key] = get_value_from_adj(s, adj_list)

    return state_value
