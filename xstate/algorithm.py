from typing import List, Set, Dict
from xstate.transition import Transition
from xstate.state_node import StateNode
from xstate.action import Action
from xstate.event import Event

def compute_entry_set(transitions: List[Transition], states_to_enter: Set[StateNode], states_for_default_entry: Set[StateNode], default_history_content: Dict):
    pass

def is_final_state(state_node: StateNode) -> bool:
    return False

def is_parallel_state(state_node: StateNode) -> bool:
    # should return whether state_node.type is parallel
    return False

def get_child_states(state_node: StateNode) -> List[StateNode]:
    return []

def is_in_final_state(state_node: StateNode) -> bool:
    pass

def enter_states(enabled_transitions: List[Transition], configuration: set, states_to_invoke: set):
    states_to_enter: Set[StateNode] = set()
    states_for_default_entry: Set[StateNode] = set()
    actions: List[Action] = []
    internal_queue: List[Event] = []

    default_history_content = {}

    compute_entry_set(enabled_transitions, states_to_enter, states_for_default_entry, default_history_content)

    for s in list(states_to_enter).sort():
        configuration.add(s)
        states_to_invoke.add(s)

        # if binding == "late" and s.isFirstEntry:
        #     initializeDataModel(datamodel.s,doc.s)
        #     s.isFirstEntry = false

        for content in s.entry.sort():
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
                if all(is_in_final_state(parent_state) for parent_state in get_child_states(grandparent)):
                    internal_queue.append(Event(f"done.state.{grandparent.id}"))


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
