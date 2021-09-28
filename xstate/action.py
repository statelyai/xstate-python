from typing import TYPE_CHECKING, Any, Callable, Dict, Optional, List, Union

if TYPE_CHECKING:
    from xstate.action import Action
    from xstate.state_node import StateNode
import logging

logger = logging.getLogger(__name__)
from xstate.event import Event

# from xstate.action_types import DoneInvoke
from xstate.types import (
    ActionFunction,
    ActionFunctionMap,
    ActionType,
    ActionTypes,
    ActionObject,
)


def not_implemented():
    logger.warning("Action function: not implemented")
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
def done_invoke(id: str, data: Any) -> DoneEvent:
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
    return DoneEvent(type, data)


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


# export function getActionFunction<TContext, TEvent extends EventObject>(
#   actionType: ActionType,
#   actionFunctionMap?: ActionFunctionMap<TContext, TEvent>
# ):
def get_action_function(
    action_type: ActionType, action_function_map: ActionFunctionMap
) -> Union[ActionObject, ActionFunction, None]:
    #   | ActionObject<TContext, TEvent>
    #   | ActionFunction<TContext, TEvent>
    #   | undefined {

    #   return actionFunctionMap
    #     ? actionFunctionMap[actionType] || undefined
    #     : undefined;
    return action_function_map[action_type] or None if action_function_map else None


# export function toActionObject<TContext, TEvent extends EventObject>(
#   action: Action<TContext, TEvent>,
#   actionFunctionMap?: ActionFunctionMap<TContext, TEvent>
# ): ActionObject<TContext, TEvent> {
def to_action_object(action: Action, action_function_map: ActionFunctionMap):
    #   let actionObject: ActionObject<TContext, TEvent>;
    action_object: ActionObject = {}

    #   if (isString(action) || typeof action === 'number') {
    if isinstance(action, str) or type(action) == "number":
        #     const exec = getActionFunction(action, actionFunctionMap);
        exec = get_action_function(action, action_function_map)

        #     if (isFunction(exec)) {
        if callable(exec):
            #       action_object = {
            #         "type": action,
            #         exec
            #       }
            action_object = {
                "type": action,
                "exec": exec,
            }
        #     } else if (exec) {
        elif exec:
            #       actionObject = exec;
            action_object = exec
        #     } else {
        else:
            #       actionObject = { type : action, exec: undefined };
            action_object = {"type": action, "exec": None}
    #     }
    #   } else if (isFunction(action)) {
    elif callable(action):
        #     actionObject = {
        #       // Convert action to string if unnamed
        #       type : action.name || action.toString(),
        #       exec: action
        #     };
        action_object = {
            # // Convert action to string if unnamed
            # "type": action.__qualname__ or str(action),
            "type": str(ActionTypes.Raise),  # "xstate:raise
            "exec": action,
        }
        action_object = {**action_object, "data": action_object.copy()}
    #   } else {
    elif isinstance(action, dict):
        action_object = {
            "type": action.get("type", ActionTypes.Raise),
            "exec": action.get("exec", None),
        }
        action_object["data"] = action if ("event" in action) else {}
    else:
        # TODO TD, some validation required that object has a type and exec attribute
        #     const exec = getActionFunction(action.type, actionFunctionMap);
        exec = get_action_function(action.type, action_function_map)
        #     if (isFunction(exec)) {
        if callable(exec):
            #       actionObject = {
            #         ...action,
            #         exec
            #       };
            action_object = {**action, **{"exec": exec}}
        #     } else if (exec) {
        elif exec:
            #       const actionType = exec.type || action.type;
            action_type = exec.type or action.type
            #       actionObject = {
            #         ...exec,
            #         ...action,
            #         type : actionType
            #       } as ActionObject<TContext, TEvent>;
            action_object = {**exec, **action, **{"type": action_type}}

        #     } else {
        else:
            #       actionObject = action as ActionObject<TContext, TEvent>;
            #     }
            #   }
            action_object = action

    #   return actionObject;
    return Action(**action_object)


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


def to_action_objects(
    action: Union[Action, List[Action]],
    action_function_map: Any,  # TODO: define types: ActionFunctionMap<TContext, TEvent>
) -> List[ActionObject]:
    if not action:
        return []
    actions = action if isinstance(action, List) else [action]

    return [to_action_object(sub_action, action_function_map) for sub_action in actions]
