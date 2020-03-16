from typing import List
from xstate.transition import Transition

# defaultHistoryContent = new HashTable()
# computeEntrySet(enabledTransitions, statesToEnter, statesForDefaultEntry, defaultHistoryContent)
# for s in statesToEnter.toList().sort(entryOrder):
#     configuration.add(s)
#     statesToInvoke.add(s)
#     if binding == "late" and s.isFirstEntry:
#         initializeDataModel(datamodel.s,doc.s)
#         s.isFirstEntry = false
#     for content in s.onentry.sort(documentOrder):
#         executeContent(content)
#     if statesForDefaultEntry.isMember(s):
#         executeContent(s.initial.transition)
#     if defaultHistoryContent[s.id]:
#         executeContent(defaultHistoryContent[s.id])
#     if isFinalState(s):
#         if isSCXMLElement(s.parent):
#             running = false
#         else:
#             parent = s.parent
#             grandparent = parent.parent
#             internalQueue.enqueue(new Event("done.state." + parent.id, s.donedata))
#             if isParallelState(grandparent):
#                 if getChildStates(grandparent).every(isInFinalState):
#                     internalQueue.enqueue(new Event("done.state." + grandparent.id))


def enter_states(enabled_transitions: List[Transition]):
    states_to_enter = set()
    states_for_default_entry = set()

