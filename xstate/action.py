from typing import TYPE_CHECKING,Any, Callable, Dict, Optional,List, Union
if TYPE_CHECKING:
    from xstate.action import Action
    from xstate.state_node import StateNode
from xstate.event import Event
# from xstate.action_types import DoneInvoke
from xstate.types import ActionTypes, ActionObject

def not_implemented():
    pass

class DoneEvent(Event):
    pass


# /**
#  * Returns an event that represents that an invoked service has terminated.
#  *
#  * An invoked service is terminated when it has reached a top-level final state node,
#  * but not when it is canceled.
#  *
#  * @param id The final state node ID
#  * @param data The data to pass into the event
#  */
# export function doneInvoke(id: string, data?: any): DoneEvent {
#   const type = `${ActionTypes.DoneInvoke}.${id}`;
#   const eventObject = {
#     type,
#     data
#   };

#   eventObject.toString = () => type;

#   return eventObject as DoneEvent;
# }
def done_invoke(id: str, data: Any)->DoneEvent: 
    """Returns an event that represents that an invoked service has terminated.
 
    * An invoked service is terminated when it has reached a top-level final state node,
    * but not when it is canceled.
 
    Args:
        id (str): The final state node ID
        data (Any): The data to pass into the event

    Returns:
        DoneEvent: an event that represents that an invoked service has terminated
    """
    type = f"{ActionTypes.DoneInvoke}.{id}"
    return DoneEvent(type,data)

# export const toActionObjects = <TContext, TEvent extends EventObject>(
#   action?: SingleOrArray<Action<TContext, TEvent>> | undefined,
#   actionFunctionMap?: ActionFunctionMap<TContext, TEvent>
# ): Array<ActionObject<TContext, TEvent>> => {
#   if (!action) {
#     return [];
#   }

#   const actions = isArray(action) ? action : [action];

#   return actions.map((subAction) =>
#     toActionObject(subAction, actionFunctionMap)
#   );
# };



class Action:
    type: str
    exec: Callable[[], None]
    data: Dict[str, Any]

    def __init__(
        self,
        type: str,
        exec: Optional[Callable[[], None]] = not_implemented,
        data: Dict[str, Any] = {},
    ):
        self.type = type
        self.exec = exec
        self.data = data

    def __repr__(self):
        return repr({"type": self.type})

def to_action_objects(
        action: Union[Action,List[Action]],
        action_function_map: Any  # TODO: define types: ActionFunctionMap<TContext, TEvent>
    )->List[ActionObject]: 
    if not action:
        return []
    actions = action if isinstance(action,List) else [action]

    return [ action_function_map(sub_action) for sub_action in actions]