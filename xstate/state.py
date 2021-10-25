from __future__ import (
    annotations,
)  #  PEP 563:__future__.annotations will become the default in Python 3.11
import logging

logger = logging.getLogger(__name__)

from typing import TYPE_CHECKING, Any, Dict, List, Set, Union
from xstate.transition import Transition

# from xstate.algorithm import get_state_value
import xstate.algorithm as algorithm
from xstate.action import init_event
from contextvars import Context
from dataclasses import dataclass

if TYPE_CHECKING:
    from xstate.action import Action
    from xstate.state_node import StateNode
    from xstate.types import (
        StateValue,
        SCXML,
    )


from anytree import Node, RenderTree, LevelOrderIter


class State:
    configuration: Set["StateNode"]
    value: str
    context: Dict[str, Any]
    actions: List["Action"]
    # TODO WIP (history) - fix types
    history_value: List[
        Any
    ]  # List["History"] #The tree representing historical values of the state nodes
    history: Any  # State  #The previous state
    transitions: List["Transition"]

    def __init__(
        self,
        configuration: Set["StateNode"],
        context: Dict[str, Any] = {},
        actions: List["Action"] = [],
        **kwargs,
    ):
        # root = next(iter(configuration)).machine.root
        self.configuration = configuration
        if kwargs.get("value", None) is None:
            if self.configuration == []:
                msg = f"A valid configuration must exist to facilitate state: obtaining state as no value given"
                logger.error(msg)
                raise Exception(msg)
            else:
                self.value = algorithm.get_state_value(
                    next(iter(configuration)).machine.root, configuration
                )

        else:
            self.value = kwargs.get("value", None)
        self.context = context
        self.actions = actions
        self.history_value = kwargs.get("history_value", None)
        self.history = kwargs.get("history", None)
        self.transitions = kwargs.get("transitions", [])

    # TODO: __repr__ and __str__ should be swapped,  __repr__ should be able to instantiate an instance

    # def __repr__(self):
    #     return repr(
    #         {
    #             "value": self.value,
    #             "context": self.context,
    #             "actions": self.actions,
    #         }
    #     )
    def __repr__(self):
        return "<State %s>" % repr(
            {
                "value": self.value,
                "context": self.context,
                "actions": self.actions,
            }
        )

    def __str__(self):
        # configuration is a set, we need an algorithm to walk the set and produce an ordered list
        # Why:  [state.id for state in self.configuration]    # produces unsorted with machine prefix `['test_states.two.deep', 'test_states.two', 'test_states.two.deep.foo']`

        # build dict of child:parent
        relationships = {
            state.id: state.parent.id if state.parent else None
            for state in self.configuration
        }
        # find root node, ie has parent and without a '.' in the parent id
        roots = [
            (child, parent)
            for child, parent in relationships.items()
            if parent and "." not in parent
        ]
        assert (
            len(roots) == 1
        ), "Invalid Root, can only be 1 root and must be at least 1 root"

        relatives = {
            child: parent
            for child, parent in relationships.items()
            if parent and "." in parent
        }
        child, parent = roots[0]
        root_node = Node(parent)
        added = {}
        added[child] = Node(child, parent=root_node)
        while relatives:
            for child, parent in relatives.items():
                if parent in added:

                    added[child] = Node(child, parent=added[parent])
                    relatives.pop(child)
                    break
                # Should have no parent as None, because we have already determined the root
                # TODO: possible should change to this as more general
                # elif parent  is None:
                #     tree.create_node(key, key)
                #     added.add(key)
                #     relatives.pop(key)
                #     break
        # Render in ascii the tree
        # for pre, fill, node in RenderTree(root_node):
        #     print("%s%s" % (pre, node.name))

        states_ordered = [node.name for node in LevelOrderIter(root_node)]
        root_state = states_ordered[0] + "."
        # ignore the root state
        states_ordered = [state.replace(root_state, "") for state in states_ordered[1:]]
        return repr(states_ordered)

        # return f"""{self.__class__.__name__}(configuration={'<WIP a Set["StateNode"]>'}, context={self.context} , actions={self.actions})"""

    #   public static from<TC, TE extends EventObject = EventObject>(
    #     stateValue: State<TC, TE, any, any> | StateValue,
    #     context?: TC | undefined
    #   ): State<TC, TE, any, any> {
    def _from(state_value: Union[State, StateValue], context: Any = None) -> State:
        """Creates a new State instance for the given `stateValue` and `context`.

        Args:
            state_value (Union[State, StateValue]): [description]
            context (Any): [description]

        Returns:
            State: [description]
        """
        # /**
        #    * Creates a new State instance for the given `stateValue` and `context`.
        #    * @param stateValue
        #    * @param context
        #    */

        #     if (stateValue instanceof State) {
        if isinstance(state_value, State):
            #       if (stateValue.context !== context) {
            if state_value.context != context:
                #         return new State<TC, TE>({
                #           value: stateValue.value,
                #           context: context as TC,
                #           _event: stateValue._event,
                #           _sessionid: null,
                #           historyValue: stateValue.historyValue,
                #           history: stateValue.history,
                #           actions: [],
                #           activities: stateValue.activities,
                #           meta: {},
                #           events: [],
                #           configuration: [], // TODO: fix,
                #           transitions: [],
                #           children: {}
                #         });
                #       }
                return State(
                    **{
                        "value": state_value.value,
                        "context": context,
                        "_event": state_value._event,
                        "_sessionid": None,
                        "historyValue": state_value.history_value,
                        "history": state_value.history,
                        "actions": [],
                        "activities": state_value.activities,
                        "meta": {},
                        "events": [],
                        "configuration": [],  # TODO: fix, ( oriiginal comment in JS) look into thoughts in JS
                        "transitions": [],
                        "children": {},
                    }
                )
            #       }

            #       return stateValue;
            return state_value
        #     }

        #     const _event = initEvent as SCXML.Event<TE>;
        # TODO capture SCXML.Event
        _event: SCXML.Event = init_event

        #     return new State<TC, TE>({
        #       value: stateValue,
        #       context: context as TC,
        #       _event,
        #       _sessionid: null,
        #       historyValue: undefined,
        #       history: undefined,
        #       actions: [],
        #       activities: undefined,
        #       meta: undefined,
        #       events: [],
        #       configuration: [],
        #       transitions: [],
        #       children: {}
        return State(
            **{
                "value": state_value,
                "context": context,
                "_event": None,
                "_sessionid": None,
                "historyValue": None,
                "history": None,
                "actions": [],
                "activities": None,
                "meta": None,
                "events": [],
                "configuration": [],
                "transitions": [],
                "children": {},
            }
        )

    #   }


# StateType = Union[str, State]
# StateValue = str
