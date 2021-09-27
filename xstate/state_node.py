from __future__ import annotations #  PEP 563:__future__.annotations will become the default in Python 3.11
from typing import TYPE_CHECKING, Dict, List, Optional, Union
import logging
logger = logging.getLogger(__name__)

from xstate import transition

from xstate.constants import  (
    STATE_DELIMITER,
    TARGETLESS_KEY,
)
from xstate.types import  (
    TransitionConfig,
    TransitionDefinition,
)

from xstate.action import Action,to_action_objects, to_action_object
from xstate.transition import Transition
from xstate.algorithm import (
    to_transition_config_array,
    to_state_path,
    flatten,
    normalize_target,
    to_array_strict,
    is_machine,
    to_array,
    to_guard,
    done,
)

from xstate.action import (
    done_invoke,
    to_action_objects
)

from xstate.environment import (
    IS_PRODUCTION,
    WILDCARD,
    STATE_IDENTIFIER,
    NULL_EVENT

)
if TYPE_CHECKING:
    from xstate.machine import Machine
    from xstate.state import State, StateValue


def is_state_id(state_id:str)->bool:
    return state_id[0] == STATE_IDENTIFIER
class StateNode:
    on: Dict[str, List[Transition]]
    machine: "Machine"
    parent: Optional["StateNode"]
    initial: Optional[Transition]
    entry: List[Action]
    exit: List[Action]
    donedata: Optional[Dict]
    type: str  # 'atomic' or 'compound' or 'parallel' or 'final'
    transitions: List[Transition]
    id: str
    key: str
    states: Dict[str, "StateNode"]

    def get_actions(self, action):
        """get_actions ( requires migration to newer implementation"""
        logger.warning("The function `get_actions` in `StateNode` , requires migration to newer `xstate.core` implementation")
        return to_action_object(action, action_function_map=None)

    # TODO migrate get_actions to current xstate.core equivilance

        #   private getActions(
        #     transition: StateTransition<TContext, TEvent>,
        #     currentContext: TContext,
        #     _event: SCXML.Event<TEvent>,
        #     prevState?: State<TContext>
        #   ): Array<ActionObject<TContext, TEvent>> {
        #     const prevConfig = getConfiguration(
        #       [],
        #       prevState ? this.getStateNodes(prevState.value) : [this]
        #     );
        #     const resolvedConfig = transition.configuration.length
        #       ? getConfiguration(prevConfig, transition.configuration)
        #       : prevConfig;

        #     for (const sn of resolvedConfig) {
        #       if (!has(prevConfig, sn)) {
        #         transition.entrySet.push(sn);
        #       }
        #     }
        #     for (const sn of prevConfig) {
        #       if (!has(resolvedConfig, sn) || has(transition.exitSet, sn.parent)) {
        #         transition.exitSet.push(sn);
        #       }
        #     }

        #     if (!transition.source) {
        #       transition.exitSet = [];

        #       // Ensure that root StateNode (machine) is entered
        #       transition.entrySet.push(this);
        #     }

        #     const doneEvents = flatten(
        #       transition.entrySet.map((sn) => {
        #         const events: DoneEventObject[] = [];

        #         if (sn.type !== 'final') {
        #           return events;
        #         }

        #         const parent = sn.parent!;

        #         if (!parent.parent) {
        #           return events;
        #         }

        #         events.push(
        #           done(sn.id, sn.doneData), // TODO: deprecate - final states should not emit done events for their own state.
        #           done(
        #             parent.id,
        #             sn.doneData
        #               ? mapContext(sn.doneData, currentContext, _event)
        #               : undefined
        #           )
        #         );

        #         const grandparent = parent.parent!;

        #         if (grandparent.type === 'parallel') {
        #           if (
        #             getChildren(grandparent).every((parentNode) =>
        #               isInFinalState(transition.configuration, parentNode)
        #             )
        #           ) {
        #             events.push(done(grandparent.id));
        #           }
        #         }

        #         return events;
        #       })
        #     );

        #     transition.exitSet.sort((a, b) => b.order - a.order);
        #     transition.entrySet.sort((a, b) => a.order - b.order);

        #     const entryStates = new Set(transition.entrySet);
        #     const exitStates = new Set(transition.exitSet);

        #     const [entryActions, exitActions] = [
        #       flatten(
        #         Array.from(entryStates).map((stateNode) => {
        #           return [
        #             ...stateNode.activities.map((activity) => start(activity)),
        #             ...stateNode.onEntry
        #           ];
        #         })
        #       ).concat(doneEvents.map(raise) as Array<ActionObject<TContext, TEvent>>),
        #       flatten(
        #         Array.from(exitStates).map((stateNode) => [
        #           ...stateNode.onExit,
        #           ...stateNode.activities.map((activity) => stop(activity))
        #         ])
        #       )
        #     ];

        #     const actions = toActionObjects(
        #       exitActions.concat(transition.actions).concat(entryActions),
        #       this.machine.options.actions
        #     ) as Array<ActionObject<TContext, TEvent>>;

        #     return actions;
        #   }

        #     def __init__(
        #         self,
        #         # { "type": "compound", "states": { ... } }
        #         config,
        #         machine: "Machine",
        #         parent: Union["StateNode", "Machine"] = None,
        #         key: str = None,

        #     ):
        #         self.config = config
        #         self.parent = parent
        #         self.id = (
        #             config.get("id", parent.id + (("." + key) if key else ""))
        #             if parent
        #             else config.get("id", machine.id + (("." + key) if key else ""))
        #         )
        #         self.entry = (
        #             [self.get_actions(entry_action) for entry_action in config.get("entry")]
        #             if config.get("entry")
        #             else []
        #         )

        #         self.exit = (
        #             [self.get_actions(exit_action) for exit_action in config.get("exit")]
        #             if config.get("exit")
        #             else []
        #         )

        #         self.key = key
        #         self.states = {
        #             k: StateNode(v, machine=machine, parent=self, key=k)
        #             for k, v in config.get("states", {}).items()
        #         }
        #         self.on = {}
        #         self.transitions = []
        #         for k, v in config.get("on", {}).items():
        #             self.on[k] = []
        #             transition_configs = v if isinstance(v, list) else [v]

        #             for transition_config in transition_configs:
        #                 transition = Transition(
        #                     transition_config,
        #                     source=self,
        #                     event=k,
        #                     order=len(self.transitions),
        #                 )
        #                 self.on[k].append(transition)
        #                 self.transitions.append(transition)

        #         self.type = config.get("type")

        #         if self.type is None:
        #             self.type = "atomic" if not self.states else "compound"

        #         if self.type == "final":
        #             self.donedata = config.get("data")

        #         if config.get("onDone"):
        #             done_event = f"done.state.{self.id}"
        #             done_transition = Transition(
        #                 config.get("onDone"),
        #                 source=self,
        #                 event=done_event,
        #                 order=len(self.transitions),
        #             )
        #             self.on[done_event] = done_transition
        #             self.transitions.append(done_transition)

        #         machine._register(self)

        #     @property
        #     def initial(self):
        #         initial_key = self.config.get("initial")

        #         if not initial_key:
        #             if self.type == "compound":
        #                 return Transition(
        #                     next(iter(self.states.values())), source=self, event=None, order=-1
        #                 )
        #         else:
        #             return Transition(
        #                 self.states.get(initial_key), source=self, event=None, order=-1
        #             )

        #     def _get_relative(self, target: str) -> "StateNode":
        #         if target.startswith("#"):
        #             return self.machine._get_by_id(target[1:])

        #         state_node = self.parent.states.get(target)

        #         if not state_node:
        #             raise ValueError(
        #                 f"Relative state node '{target}' does not exist on state node '#{self.id}'"  # noqa
        #             )

        #         return state_node
            #

    def __init__(
        self,
        # { "type": "compound", "states": { ... } }
        config,
        machine: "Machine",
        parent: Union["StateNode", "Machine"] = None,
        key: str = None,

    ):
        self.config = config
        self.parent = parent
        self.id = (
            config.get("id", parent.id + (("." + key) if key else ""))
            if parent
            else config.get("id", machine.id + (("." + key) if key else ""))
        )
        self.entry = (
            [self.get_actions(entry_action) for entry_action in config.get("entry")]
            if config.get("entry")
            else []
        )

        self.exit = (
            [self.get_actions(exit_action) for exit_action in config.get("exit")]
            if config.get("exit")
            else []
        )

        self.key = key
        self.states = {
            k: StateNode(v, machine=machine, parent=self, key=k)
            for k, v in config.get("states", {}).items()
        }
        self.on = {}
        self.transitions = []
        for k, v in config.get("on", {}).items():
            self.on[k] = []
            transition_configs = v if isinstance(v, list) else [v]

            for transition_config in transition_configs:
                transition = Transition(
                    transition_config,
                    source=self,
                    event=k,
                    order=len(self.transitions),
                )
                self.on[k].append(transition)
                self.transitions.append(transition)

        self.type = config.get("type")

        if self.type is None:
            self.type = "atomic" if not self.states else "compound"

        if self.type == "final":
            self.donedata = config.get("data")

        if config.get("onDone"):
            done_event = f"done.state.{self.id}"
            done_transition = Transition(
                config.get("onDone"),
                source=self,
                event=done_event,
                order=len(self.transitions),
            )
            self.on[done_event] = done_transition
            self.transitions.append(done_transition)

        machine._register(self)

    @property
    def initial(self):
        initial_key = self.config.get("initial")

        if not initial_key:
            if self.type == "compound":
                return Transition(
                    next(iter(self.states.values())), source=self, event=None, order=-1
                )
        else:
            return Transition(
                self.states.get(initial_key), source=self, event=None, order=-1
            )

    def _get_relative(self, target: str) -> "StateNode":
        if target.startswith("#"):
            return self.machine._get_by_id(target[1:])

        state_node = self.parent.states.get(target)

        if not state_node:
            raise ValueError(
                f"Relative state node '{target}' does not exist on state node '#{self.id}'"  # noqa
            )

        return state_node

# const validateArrayifiedTransitions = <TContext>(
#   stateNode: StateNode<any, any, any, any>,
#   event: string,
#   transitions: Array<
#     TransitionConfig<TContext, EventObject> & {
#       event: string;
#     }
#   >
# ) => {
def validate_arrayified_transitions(
      state_node: StateNode,
      event: str,
      transitions: List[TransitionConfig],
          #   TContext, EventObject> & {
    #       event: string;
    #     }
    #   >
):

#   const hasNonLastUnguardedTarget = transitions
#     .slice(0, -1)
#     .some(
#       (transition) =>
#         !('cond' in transition) &&
#         !('in' in transition) &&
#         (isString(transition.target) || isMachine(transition.target))
#     );
    has_non_last_unguarded_target = any([( 
            'cond' not in transition 
            and 'in' not in transition
            and (isinstance(transition.target,str) or is_machine(transition.target)))
                for transition in transitions[0:-1]])


    # .slice(0, -1)
    # .some(
    #   (transition) =>
    #     !('cond' in transition) &&
    #     !('in' in transition) &&
    #     (isString(transition.target) || isMachine(transition.target))
    # );

#   const eventText =
#     event === NULL_EVENT ? 'the transient event' : `event '${event}'`;
    eventText =  'the transient event' if event == NULL_EVENT else  f"event '{event}'"

#   warn(
#     !hasNonLastUnguardedTarget,
#     `One or more transitions for ${eventText} on state '${stateNode.id}' are unreachable. ` +
#       `Make sure that the default transition is the last one defined.`
#   );
    if not has_non_last_unguarded_target: logger.warning((
        f"One or more transitions for {eventText} on state '{state_node.id}' are unreachable. "
        f"Make sure that the default transition is the last one defined."
    ))



#  /**
#    * Returns the relative state node from the given `statePath`, or throws.
#    *
#    * @param statePath The string or string array relative path to the state node.
#    */
#   public getStateNodeByPath(
#     statePath: string | string[]
#   ): StateNode<TContext, any, TEvent, any> {


def get_state_node_by_path(self,
            state_path: str
        ) -> StateNode:
    """ Returns the relative state node from the given `statePath`, or throws.

    Args:
        statePath (string):The string or string array relative path to the state node.

    Raises:
        Exception: [??????]

    Returns:
        StateNode: the relative state node from the given `statePath`, or throws.
    """



        #     if (typeof statePath === 'string' && isStateId(statePath)) {
        #       try {
        #         return this.getStateNodeById(statePath.slice(1));
        #       } catch (e) {
        #         // try individual paths
        #         // throw e;
        #       }
        #     }

    if (isinstance(state_path,str) and is_state_id(state_path)):
        try:
            return self.get_state_node_by_id(state_path[1:].copy())
        except Exception as e:
            # // try individual paths
            # // throw e;
            pass

        #     const arrayStatePath = toStatePath(statePath, this.delimiter).slice();
        array_state_path = to_state_path(state_path, self.delimiter)[:].copy()
        #     let currentStateNode: StateNode<TContext, any, TEvent, any> = this;
        current_state_node= self

        #     while (arrayStatePath.length) {
        while len(array_state_path)>0:
        #       const key = arrayStatePath.shift()!;
            key = array_state_path.pop() # TODO check equivaelance to js .shift()! , https://www.typescriptlang.org/docs/handbook/release-notes/typescript-2-0.html#non-null-assertion-operator
        #       if (!key.length) {
        #         break;
        #       }

            if len(key)==0:
                break

        #       currentStateNode = currentStateNode.getStateNode(key);
            current_state_node = current_state_node.get_state_node(key)

        #     return currentStateNode;
        return current_state_node

    #   private resolveTarget(
    #     _target: Array<string | StateNode<TContext, any, TEvent>> | undefined
    #   ): Array<StateNode<TContext, any, TEvent>> | undefined {

    def resolve_target(
        _target: List[StateNode] 
      )-> List[StateNode]: 


        #     if (_target === undefined) {
        #       // an undefined target signals that the state node should not transition from that state when receiving that event
        #       return undefined;
        #     }
        if not _target:
            #    an undefined target signals that the state node should not transition from that state when receiving that event
            return None
            


        #     return _target.map((target) => 
        def function(self,target):
            #       if (!isString(target)) {
            #         return target;
            #       }
            if isinstance(target,str):
                return target

            #       const isInternalTarget = target[0] === this.delimiter;
            is_internal_target = target[0] == self.delimiter
            

            #       // If internal target is defined on machine,
            #       // do not include machine key on target
            #       if (isInternalTarget && !this.parent) {
            #         return this.getStateNodeByPath(target.slice(1));
            #       }
            # If internal target is defined on machine,
            # do not include machine key on target
            if (is_internal_target and  not self.parent):
                return self.get_state_node_by_path(target.slice(1))

            #       const resolvedTarget = isInternalTarget ? this.key + target : target;
            resolved_target = self.key + target if is_internal_target else target

            #       if (this.parent) {
            #         try {
            #           const targetStateNode = this.parent.getStateNodeByPath(
            #             resolvedTarget
            #           );
            #           return targetStateNode;
            #         } catch (err) {
            #           throw new Error(
            #             `Invalid transition definition for state node '${this.id}':\n${err.message}`
            #           );
            #         }

            if (self.parent):
                try:
                    target_state_node = self.parent.get_state_node_by_path(
                                resolved_target
                                )
                    return target_state_node
                except Exception as e:
                    msg=f"Invalid transition definition for state node '{self.id}':\n{e}"
                    logger.error(msg)
                    raise Exception(msg)
            #       } else {
            #         return this.getStateNodeByPath(resolvedTarget);
            else:
                return self.get_state_node_by_path(resolved_target)


    #   private formatTransition(
    #     transitionConfig: TransitionConfig<TContext, TEvent> & {
    #       event: TEvent['type'] | NullEvent['type'] | '*';
    #     }
    #   ): TransitionDefinition<TContext, TEvent> {

    def format_transition(self,
            transition_config: TransitionConfig
            )->TransitionDefinition:

        #     const normalizedTarget = normalizeTarget(transitionConfig.target);
        normalized_target = normalize_target(transition_config['target'])

        #     const internal =
        #       'internal' in transitionConfig
        #         ? transitionConfig.internal
        #         : normalizedTarget
        #         ? normalizedTarget.some(
        #             (_target) => isString(_target) && _target[0] === this.delimiter
        #           )
        #         : true;
        internal = transition_config['internal'] \
                        if 'internal' in transition_config else \
                        any(isinstance(_target,str) and _target[0] == self.delimiter for _target in normalized_target) \
                        if normalized_target else True

        #     const { guards } = this.machine.options;
        guards  = self.machine.options['guards']
        #     const target = this.resolveTarget(normalizedTarget);
        target = self.resolve_target(normalized_target)

        #     const transition = {
        #       ...transitionConfig,
        #       actions: toActionObjects(toArray(transitionConfig.actions)),
        #       cond: toGuard(transitionConfig.cond, guards),
        #       target,
        #       source: this as any,
        #       internal,
        #       eventType: transitionConfig.event,
        #       toJSON: () => ({
        #         ...transition,
        #         target: transition.target
        #           ? transition.target.map((t) => `#${t.id}`)
        #           : undefined,
        #         source: `#${this.id}`
        #       })
        #     };
        transition = {
            **transition_config,
            **{
            "actions": to_action_objects(to_array(transition_config['actions'])),
            "cond": to_guard(transition_config.cond, guards),
            **target,
            "source": self ,
            **internal,
            "eventType": transition_config.event,
            "toJSON": None
            }}
        transition = {
            **transition,
            **{
                "target":["#{t.id}" for t in transition.target] if  transition.target else None,
                "source": "#{self.id}"
            }}


        #     return transition;
        return transition


    def format_transitions(self)->List:
#   StateNode.prototype.formatTransitions = function () {
#     var e_9, _a;

#     var _this = this;
        _self = self

        onConfig=None   

        #     if (!this.config.on) {
        #       onConfig = [];
        if 'on' not in self.config:
            onConfig = {}

        #     } else if (Array.isArray(this.config.on)) {
        #       onConfig = this.config.on;
        elif isinstance(self.config,dict):
            onConfig = self.config['on']
        #     } else {
        else:
            #TODO: TD implement WILDCARD
        #       var _b = this.config.on,
        #           _c = WILDCARD,
        #           _d = _b[_c],
        #           wildcardConfigs = _d === void 0 ? [] : _d,
            wildcard_configs = [] # Workaround for #TODO: TD implement WILDCARD
        #           strictTransitionConfigs_1 = _tslib.__rest(_b, [typeof _c === "symbol" ? _c : _c + ""]);
            #TODO: TD implement and tslib.__rest functionationality
            # strictTransitionConfigs_1 = _tslib.__rest(_b, [typeof _c === "symbol" ? _c : _c + ""])
            strict_transition_configs_1 = self.config['on']

            # if (!environment.IS_PRODUCTION && key === NULL_EVENT) {
            def function(key):
                # function (key) {
                #         if (!environment.IS_PRODUCTION && key === NULL_EVENT) {
                #           utils.warn(false, "Empty string transition configs (e.g., `{ on: { '': ... }}`) for transient transitions are deprecated. Specify the transition in the `{ always: ... }` property instead. " + ("Please check the `on` configuration for \"#" + _this.id + "\"."));
                #         }

                #         var transitionConfigArray = utils.toTransitionConfigArray(key, strictTransitionConfigs_1[key]);

                #         if (!environment.IS_PRODUCTION) {
                #           validateArrayifiedTransitions(_this, key, transitionConfigArray);
                #         }

                #         return transitionConfigArray;
                #       }                if IS_PRODUCTION and not key: 
                logger.warning((
                    f"Empty string transition configs (e.g., `{{ on: {{ '': ... }}}}`) for transient transitions are deprecated. "
                    f"Specify the transition in the `{{ always: ... }}` property instead. "
                    f"Please check the `on` configuration for \"#{self.id}\"."
                ))
                transition_config_array = to_transition_config_array(key, strict_transition_configs_1[key])

                if not IS_PRODUCTION:
                    validate_arrayified_transitions(self, key, transition_config_array)
                

                return transition_config_array

        #       onConfig = utils.flatten(utils.keys(strictTransitionConfigs_1).map(
        # ).concat(utils.toTransitionConfigArray(WILDCARD, wildcardConfigs)));
        #     }

        on_config = flatten([function(key) for key in strict_transition_configs_1.keys()].append(
                        to_transition_config_array(WILDCARD, wildcard_configs)
        ))

        #     var eventlessConfig = this.config.always ? utils.toTransitionConfigArray('', this.config.always) : [];
        eventless_config = to_transition_config_array('', self.config['always']) if 'always' in self.config else []

        #     var doneConfig = this.config.onDone ? utils.toTransitionConfigArray(String(actions.done(this.id)), this.config.onDone) : [];
        done_config = to_transition_config_array(str(done(self.id)), self.config['onDone']) if 'onDone' in self.config else []

        #     if (!environment.IS_PRODUCTION) {
        #       utils.warn(!(this.config.onDone && !this.parent), "Root nodes cannot have an \".onDone\" transition. Please check the config of \"" + this.id + "\".");
        #     }
        if (IS_PRODUCTION
            and not ('onDone' in self.config and not self.parent)):

            logger.warning(f"Root nodes cannot have an \".onDone\" transition. Please check the config of \"{self.id}\".")


        def function(invoke_def):
            #     const settleTransitions: any[] = [];
            settle_transitions = []
            #     if (invokeDef.onDone) {
            if "onDone" in invoke_def:
            #       settleTransitions.push(
            #         ...toTransitionConfigArray(
            #           String(doneInvoke(invokeDef.id)),
            #           invokeDef.onDone
            #         )
            #       );
            #     }

                settle_transitions.append(
                    to_transition_config_array(
                        str(done_invoke(invoke_def.id)),
                        invoke_def['onDone'])
                        )
            #     if (invokeDef.onError) {
            if "onError" in invoke_def:
            #       settleTransitions.push(
            #         ...toTransitionConfigArray(
            #           String(error(invokeDef.id)),
            #           invokeDef.onError
            #         )
            #       );
            #     }
                settle_transitions.append(
                    to_transition_config_array(
                        str(done_invoke(invoke_def.id)),
                        invoke_def['onError'])
                        )
            #       return settleTransitions;
            return settle_transitions

        # const invokeConfig = flatten(
        #   this.invoke.map((invokeDef) => {
        invoke_config = flatten([function(element) for element in self.invoke])




        #     var delayedTransitions = this.after;
        delayed_transitions = self.after


        # const formattedTransitions = flatten(
        #   [...doneConfig, ...invokeConfig, ...onConfig, ...eventlessConfig].map(
        formatted_transitions = flatten([
        #       toArray(transitionConfig).map((transition) =>
        #         this.formatTransition(transition)
        
                self.format_transition(transition) for transition in [transition_config  

        #     (
        #       transitionConfig: TransitionConfig<TContext, TEvent> & {
        #         event: TEvent['type'] | NullEvent['type'] | '*';
        #       }
        #     ) =>
                
                for transition_config in [done_config, invoke_config, on_config, eventless_config]]

        ])
        

        # for (const delayedTransition of delayedTransitions) {
        #   formattedTransitions.push(delayedTransition as any);
        # }
        for delayed_transition in delayed_transitions:
            formatted_transitions.append(delayed_transition)
        
        [formatted_transitions.append(delayed_transition) for delayed_transition in  delayed_transitions ]
        

        return formatted_transitions

    #   Object.defineProperty(StateNode.prototype, "transitions", {
    @property
    def transitions(self) -> List:
    #     /**
    #      * All the transitions that can be taken from this state node.
    #      */
    #     get: function () {
    #       return this.__cache.transitions || (this.__cache.transitions = this.formatTransitions(), this.__cache.transitions);
    #     },
        if not self.__cache.transitions:
            self.__cache.transitions = self.format_transitions()
        return self.__cache.transitions 

    #     enumerable: false,
    #     configurable: true
    #   });

    def get_state_nodes(state: Union[StateValue, State])->List["StateNode"]:
        """Returns the state nodes represented by the current state value.

        Args:
            state (Union[StateValue, State]): The state value or State instance

        Returns:
            List[StateNode]: list of state nodes represented by the current state value.
        """


        if not state:
            return []
        

    #     stateValue = state.value if isinstance(state,State) \
    #                                 else toStateValue(state, this.delimiter);

    #     if (isString(stateValue)) {
    #     const initialStateValue = this.getStateNode(stateValue).initial;

    #     return initialStateValue !== undefined
    #         ? this.getStateNodes({ [stateValue]: initialStateValue } as StateValue)
    #         : [this, this.states[stateValue]];
    #     }

    #     const subStateKeys = keys(stateValue);
    #     const subStateNodes: Array<
    #     StateNode<TContext, any, TEvent, TTypestate>
    #     > = subStateKeys.map((subStateKey) => this.getStateNode(subStateKey));

    #     subStateNodes.push(this);

    #     return subStateNodes.concat(
    #     subStateKeys.reduce((allSubStateNodes, subStateKey) => {
    #         const subStateNode = this.getStateNode(subStateKey).getStateNodes(
    #         stateValue[subStateKey]
    #         );

    #         return allSubStateNodes.concat(subStateNode);
    #     }, [] as Array<StateNode<TContext, any, TEvent, TTypestate>>)
    #     );
    # }


    # TODO: __repr__ and __str__ should be swapped,  __repr__ should be able to instantiate an instance
    # def __repr__(self) -> str:
    #      return "<StateNode %s>" % repr({"id": self.id})
    def __repr__(self) -> str:
         return "<StateNode %s>" % repr({"id": self.id, "parent": self.parent})
    def __str__(self) -> str:
        return (
            f"""{self.__class__.__name__}(config={'<WIP a Set["StateNode"]>'}, """ 
            f"""machine={self.machine}, id={self.id}, parent={self.parent})"""
        )