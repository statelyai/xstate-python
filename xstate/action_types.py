# import { ActionTypes } from './types';
from xstate.types import ActionTypes

# // xstate-specific action types
# export const start = ActionTypes.Start;
# export const stop = ActionTypes.Stop;
# export const raise = ActionTypes.Raise;
# export const send = ActionTypes.Send;
# export const cancel = ActionTypes.Cancel;
# export const nullEvent = ActionTypes.NullEvent;
# export const assign = ActionTypes.Assign;
# export const after = ActionTypes.After;
# export const doneState = ActionTypes.DoneState;
# export const log = ActionTypes.Log;
# export const init = ActionTypes.Init;
# export const invoke = ActionTypes.Invoke;
# export const errorExecution = ActionTypes.ErrorExecution;
# export const errorPlatform = ActionTypes.ErrorPlatform;
# export const error = ActionTypes.ErrorCustom;
# export const update = ActionTypes.Update;
# export const choose = ActionTypes.Choose;
# export const pure = ActionTypes.Pure;


# xstate-specific action types
start = ActionTypes.Start
stop = ActionTypes.Stop
action_raise = ActionTypes.Raise  # raise not permitted as is  python keyword
send = ActionTypes.Send
cancel = ActionTypes.Cancel
nullEvent = ActionTypes.NullEvent
assign = ActionTypes.Assign
after = ActionTypes.After
doneState = ActionTypes.DoneState
log = ActionTypes.Log
init = ActionTypes.Init
invoke = ActionTypes.Invoke
errorExecution = ActionTypes.ErrorExecution
errorPlatform = ActionTypes.ErrorPlatform
error = ActionTypes.ErrorCustom
update = ActionTypes.Update
choose = ActionTypes.Choose
pure = ActionTypes.Pure
