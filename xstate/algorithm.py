from typing import List, Set, Dict, Optional
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
                            s,
                            states_to_enter=states_to_enter,
                            states_for_default_entry=states_for_default_entry,
                            default_history_content=default_history_content,
                            history_value=history_value,
                        )


def is_history_state(state: StateNode) -> bool:
    return state.type == "history"


def is_compound_state(state: StateNode) -> bool:
    return state.type == "compound"


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
    for anc in get_proper_ancestors(state_list[0], ancestor=None):
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
    for anc in get_proper_ancestors(state, ancestor=ancestor):
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
    state: StateNode, ancestor: Optional[StateNode]
) -> Set[StateNode]:
    # this should be a set.... I forgot to return anything
    return set()


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
) -> (Set[StateNode],):
    states_to_enter: Set[StateNode] = set()
    states_for_default_entry: Set[StateNode] = set()
    actions: List[Action] = []
    internal_queue: List[Event] = []

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
        for actions in s.entry:
            # do not execute; add to actions
            for action in actions:
                actions.append(action)
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

    return (configuration,)


# procedure enterStates(enabledTransitions):
#     statesToEnter = new OrderedSet()
#     statesForDefaultEntry = new OrderedSet()
#     // initialize the temporary table for default content in history states
#     defaultHistoryContent = new HashTable()
#     computeEntrySet(enabledTransitions, statesToEnter, statesForDefaultEntry, defaultHistoryContent)
#     for s in statesToEnter.toList().sort(entryOrder):
#         configuration.add(s)
#         statesToInvoke.add(s)
#         if binding == "late" and s.isFirstEntry:
#             initializeDataModel(datamodel.s,doc.s)
#             s.isFirstEntry = false
#         for content in s.onentry.sort(documentOrder):
#             executeContent(content)
#         if statesForDefaultEntry.isMember(s):
#             executeContent(s.initial.transition)
#         if defaultHistoryContent[s.id]:
#             executeContent(defaultHistoryContent[s.id])
#         if isFinalState(s):
#             if isSCXMLElement(s.parent):
#                 running = false
#             else:
#                 parent = s.parent
#                 grandparent = parent.parent
#                 internalQueue.enqueue(new Event("done.state." + parent.id, s.donedata))
#                 if isParallelState(grandparent):
#                     if getChildStates(grandparent).every(isInFinalState):
#                         internalQueue.enqueue(new Event("done.state." + grandparent.id))
