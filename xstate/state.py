from typing import TYPE_CHECKING, Any, Dict, List, Set, Union
from xstate.transition import Transition

from xstate.algorithm import get_state_value

if TYPE_CHECKING:
    from xstate.action import Action
    from xstate.state_node import StateNode
    # TODO WIP (history) - 
    # from xstate.???? import History



class State:
    configuration: Set["StateNode"]
    value: str
    context: Dict[str, Any]
    actions: List["Action"]
    # TODO WIP (history) - fix types
    history_value: List[Any] # List["History"] #The tree representing historical values of the state nodes
    history: Any #State  #The previous state    
    transitions: List["Transition"]
    def __init__(
        self,
        configuration: Set["StateNode"],
        context: Dict[str, Any],
        actions: List["Action"] = [],
        **kwargs
    ):
        root = next(iter(configuration)).machine.root
        self.configuration = configuration
        self.value = get_state_value(root, configuration)
        self.context = context
        self.actions = actions
        self.history_value = kwargs.get("history_value",None)
        self.history = kwargs.get("history",None)
        self.transitions = kwargs.get("transitions",[])

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
        return f"""{self.__class__.__name__}(configuration={'<WIP a Set["StateNode"]>'}, context={self.context} , actions={self.actions})"""

StateType = Union[str, State]