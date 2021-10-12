from __future__ import (
    annotations,
)  #  PEP 563:__future__.annotations will become the default in Python 3.11
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union
import logging

logger = logging.getLogger(__name__)
from functools import reduce

from xstate import transition

from xstate.constants import (
    STATE_DELIMITER,
    TARGETLESS_KEY,
)
from xstate.types import (
    TransitionConfig,
    TransitionDefinition,
    HistoryValue,
    HistoryStateNodeConfig,
)  # , StateLike

from xstate.action import Action, to_action_objects, to_action_object
from xstate.transition import Transition
from xstate.algorithm import (
    to_transition_config_array,
    to_state_path,
    path_to_state_value,
    flatten,
    map_values,
    map_filter_values,
    nested_path,
    normalize_target,
    to_array_strict,
    to_state_value,
    to_state_paths,
    is_machine,
    is_leaf_node,
    is_in_final_state,
    to_array,
    to_guard,
    done,
    get_configuration,
)

from xstate.action import done_invoke, to_action_objects

from xstate.environment import IS_PRODUCTION, WILDCARD, STATE_IDENTIFIER, NULL_EVENT

if TYPE_CHECKING:
    from xstate.machine import Machine
    from xstate.types import State, StateValue, StateLike, EMPTY_OBJECT


from xstate.state import State


def is_state_id(state_id: str) -> bool:
    return state_id[0] == STATE_IDENTIFIER


# TODO TD implement __cache possibly in dataclass
#   private __cache = {
#     events: undefined as Array<TEvent['type']> | undefined,
#     relativeValue: new Map() as Map<StateNode<TContext>, StateValue>,
#     initialStateValue: undefined as StateValue | undefined,
#     initialState: undefined as State<TContext, TEvent> | undefined,
#     on: undefined as TransitionDefinitionMap<TContext, TEvent> | undefined,
#     transitions: undefined as
#       | Array<TransitionDefinition<TContext, TEvent>>
#       | undefined,
#     candidates: {} as {
#       [K in TEvent['type'] | NullEvent['type'] | '*']:
#         | Array<
#             TransitionDefinition<
#               TContext,
#               K extends TEvent['type']
#                 ? Extract<TEvent, { type: K }>
#                 : EventObject
#             >
#           >
#         | undefined;
#     },
#     delayedTransitions: undefined as
#       | Array<DelayedTransitionDefinition<TContext, TEvent>>
#       | undefined
#   };


class StateNode:
    on: Dict[str, List[Transition]]
    machine: "Machine"
    parent: Optional["StateNode"]
    initial: Union[StateValue, str]
    entry: List[Action]
    exit: List[Action]
    donedata: Optional[Dict]
    type: str  # 'atomic' or 'compound' or 'parallel' or 'final'
    transitions: List[Transition]
    id: str
    key: str
    path: List[str] = []
    states: Dict[str, "StateNode"]
    delimiter: str = STATE_DELIMITER
    __cache: Any  # TODO TD see above JS and TODO for implement __cache

    def get_actions(self, action):
        """get_actions ( requires migration to newer implementation"""
        logger.warning(
            "The function `get_actions` in `StateNode` , requires migration to newer `xstate.core` implementation"
        )
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
        parent: Union["StateNode", "Machine", None] = None,
        key: str = None,
    ):
        self.config = config
        # TODO: validate this change, initial was showing up as an event, but xstate.core has it initialized to config.initial
        # {'event': None, 'source': 'd4', 'target': ['#e3'], 'cond': None, 'actions': [], 'type': 'external', 'order': -1}
        self.history = self.config.get("history", None)
        self.initial = self.config.get("initial", None)
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

        self.key = (
            key
            or self.config.get("key", None)
            # or self.options._key or
            or self.config.get("id", None)
            or "(machine)"
        )
        self.path = self.parent.path + [self.key] if self.parent else []
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

    #   public resolve(stateValue: StateValue): StateValue {
    def resolve(self, state_value: StateValue) -> StateValue:
        """Resolves a partial state value with its full representation in this machine.

        Args:
            state_value (StateValue): The partial state value to resolve.

        Raises:
            Exception: [description]
            Exception: [description]
            ValueError: [description]
            Exception: [description]
            Exception: [description]
            Exception: [description]
            Exception: [description]

        Returns:
            StateValue: Full representation of a state in this machine.
        """
        #     if (!stateValue) {
        #       return this.initialStateValue || EMPTY_OBJECT; // TODO: type-specific properties
        #     }

        if state_value is None:
            return (
                self.initial_state_value or EMPTY_OBJECT
            )  # // TODO: type-specific properties

        #     switch (this.type) {
        #       case 'parallel':
        if self.type == "parallel":
            # return map_values(
            #           this.initialStateValue as Record<string, StateValue>,
            # self.initial_state_value,
            #           (subStateValue, subStateKey) => {
            #             return subStateValue
            #               ? this.getStateNode(subStateKey).resolve(
            #                   stateValue[subStateKey] || subStateValue
            #                 )
            #               : EMPTY_OBJECT;
            #           }
            #         );

            def func1(sub_state_value, sub_state_key):
                return (
                    self.get_state_node(sub_state_key).resolve(
                        state_value.get(sub_state_key, sub_state_value)
                    )
                    if (sub_state_value is not None)
                    else EMPTY_OBJECT
                )

            return map_values(self.initial_state_value, func1)

        #       case 'compound':
        elif self.type == "compound":
            #         if (isString(stateValue)) {
            #           const subStateNode = this.getStateNode(stateValue);

            if isinstance(state_value, str):
                sub_state_node = self.get_state_node(state_value)
                #           if (
                #             subStateNode.type === 'parallel' ||
                #             subStateNode.type === 'compound'
                #           ) {
                #             return { [stateValue]: subStateNode.initialStateValue! };
                #           }

                #           return stateValue;
                #         }

                if (
                    sub_state_node.type == "parallel"
                    or sub_state_node.type == "compound"
                ):
                    # TODO: should this be a copy, see JS !, what types is StateValue ? copy does not work for str
                    # return {[state_value]: sub_state_node.initial_state_value.copy()}
                    return {state_value: sub_state_node.initial_state_value}

                return state_value

            #         if (!keys(stateValue).length) {
            #           return this.initialStateValue || {};
            #         }

            if len(state_value.keys()) == 0:
                return self.initial_state_value if self.initial_state_value else {}

            #         return mapValues(stateValue, (subStateValue, subStateKey) => {
            #           return subStateValue
            #             ? this.getStateNode(subStateKey as string).resolve(subStateValue)
            #             : EMPTY_OBJECT;
            #         });
            def func(*args):
                sub_state_value, sub_state_key = args[0:2]
                return (
                    self.get_state_node(sub_state_key).resolve(sub_state_value)
                    if (sub_state_value is not None)
                    else EMPTY_OBJECT
                )

            return map_values(state_value, func)

        #       default:
        #         return stateValue || EMPTY_OBJECT;
        else:
            return state_value if state_value is not None else EMPTY_OBJECT
        #     }
        #   }

        #     }

        #   }

        #   public resolveState(
        #     state: State<TContext, TEvent, any, any>
        #   ): State<TContext, TEvent, TStateSchema, TTypestate> {

    def resolve_state(self, state: State) -> State:
        """Resolves the given `state` to a new `State` instance relative to this machine.

            This ensures that `.events` and `.nextEvents` represent the correct values.

        Args:
            state (State): The state to resolve

        Returns:
            State: a new `State` instance relative to this machine
        """

        #     const configuration = Array.from(
        #       getConfiguration([], this.getStateNodes(state.value))
        #     );
        # TODO: check this , is Array.from() required
        configuration = list(get_configuration([], self.get_state_nodes(state.value)))

        #     return new State({
        #       ...state,
        #       value: this.resolve(state.value),
        #       configuration,
        #       done: isInFinalState(configuration, this)
        #     });
        #   }
        return State(
            **{
                **vars(state),
                **{
                    "value": self.resolve(state.value),
                    "configuration": configuration,
                    "done": is_in_final_state(configuration, self),
                },
            }
        )
        #   }

    #   StateNode.prototype.getStateNodeById = function (stateId) {
    def get_state_node_by_id(self, state_id: str):
        """Returns the state node with the given `state_id`, or raises exception.

        Args:
            state_id (str): The state ID. The prefix "#" is removed.

        Raises:
            Exception: [description]

        Returns:
            StateNode: the state node with the given `state_id`, or raises exception.

        """
        #     var resolvedStateId = isStateId(stateId) ? stateId.slice(STATE_IDENTIFIER.length) : stateId;
        resolved_state_id = (
            state_id[len(STATE_IDENTIFIER)] if is_state_id(state_id) else state_id
        )

        #     if (resolvedStateId === this.id) {
        #       return this;
        #     }
        if resolved_state_id == self.id:
            return self

        #     var stateNode = this.machine.idMap[resolvedStateId];
        state_node = self.machine._id_map[resolved_state_id]

        #     if (!stateNode) {
        #       throw new Error("Child state node '#" + resolvedStateId + "' does not exist on machine '" + this.id + "'");
        #     }
        if not state_node:
            msg = f"Child state node '#{resolved_state_id}' does not exist on machine '{self.id}'"
            logger.error(msg)
            raise Exception(msg)

        #     return stateNode;
        return state_node

    #   };

    #   private getResolvedPath(stateIdentifier: string): string[] {
    def _get_resolved_path(self, state_identifier: str) -> List[str]:
        #     if (isStateId(stateIdentifier)) {
        if is_state_id(state_identifier):
            #       const stateNode = this.machine.idMap[
            #         stateIdentifier.slice(STATE_IDENTIFIER.length)
            #       ];
            state_node = self.machine.id_map[state_identifier[len(STATE_IDENTIFIER) :]]

            if state_node is None:
                #         throw new Error(`Unable to find state node '${stateIdentifier}'`);
                msg = f"Unable to find state node '{state_identifier}'"
                logger.error(msg)
                raise Exception(msg)
            #       return stateNode.path;
            return state_node.path
        #     return toStatePath(stateIdentifier, this.delimiter);
        return to_state_path(state_identifier, self.delimiter)

    #   }

    #   private resolveTarget(
    #     _target: Array<string | StateNode<TContext, any, TEvent>> | undefined
    #   ): Array<StateNode<TContext, any, TEvent>> | undefined {

    @property
    def initial_transition(self):
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

    #   public get initialStateNodes(): Array<StateNode<TContext, any, TEvent, any>> {
    @property
    def initial_state_nodes(self) -> List[StateNode]:

        #     if (isLeafNode(this)) {
        #       return [this];
        #     }
        if is_leaf_node(self):
            return [self]

        #     // Case when state node is compound but no initial state is defined
        #     if (this.type === 'compound' && !this.initial) {
        #       if (!IS_PRODUCTION) {
        #         warn(false, `Compound state node '${this.id}' has no initial state.`);
        #       }
        #       return [this];
        #     }

        # Case when state node is compound but no initial state is defined
        if self.type == "compound" and not self.initial:
            if not IS_PRODUCTION:
                logger.warning(
                    f"Compound state node '${self.id}' has no initial state."
                )
            return [self]

        #     const initialStateNodePaths = toStatePaths(this.initialStateValue!);
        #     return flatten(
        #       initialStateNodePaths.map((initialPath) =>
        #         this.getFromRelativePath(initialPath)
        #       )
        #     );
        #   }

        initial_state_node_paths = to_state_paths(self.initial_state_value)
        return flatten(
            [
                self.get_from_relative_path(initial_path)
                for initial_path in initial_state_node_paths
            ]
        )

    #   private get initialStateValue(): StateValue | undefined {
    @property
    def initial_state_value(self) -> Union[StateValue, None]:
        #     if (this.__cache.initialStateValue) {
        #       return this.__cache.initialStateValue;
        #     }

        # TODO: implement cache
        # if self.__cache.initial_state_value is not None:
        #     return self.__cache.initial_state_value

        #     let initialStateValue: StateValue | undefined;
        initial_state_value: Union[StateValue, None] = None

        #     if (this.type === 'parallel') {
        #       initialStateValue = mapFilterValues(
        #         this.states as Record<string, StateNode<TContext, any, TEvent>>,
        #         (state) => state.initialStateValue || EMPTY_OBJECT,
        #         (stateNode) => !(stateNode.type === 'history')
        #       );
        if self.type == "parallel":
            # TODO: wip
            initial_state_value = {
                key: state.initial_state_value
                if state.initial_state_value is not None
                else EMPTY_OBJECT
                for key, state in self.states.items()
                # for state in (
                #     self.states
                #     if not isinstance(self.states, dict)
                #     else [state_node for key, state_node in self.states.items()]
                # )
                if state.type != "history"
            }

        #     } else if (this.initial !== undefined) {
        #       if (!this.states[this.initial]) {
        #         throw new Error(
        #           `Initial state '${this.initial}' not found on '${this.key}'`
        #         );
        #       }
        elif self.initial is not None:
            if self.states.get(self.initial, None) is None:
                msg = f"Initial state '{self.initial}' not found on '{self.key}'"
                logger.error(msg)
                raise Exception(msg)
            #       initialStateValue = (isLeafNode(this.states[this.initial])
            #         ? this.initial
            #         : {
            #             [this.initial]: this.states[this.initial].initialStateValue
            #           }) as StateValue;
            initial_state_value = (
                self.initial
                if is_leaf_node(self.states[self.initial])
                else {self.initial: self.states[self.initial].initial_state_value}
            )  # StateValue

        #     } else {
        #       // The finite state value of a machine without child states is just an empty object
        #       initialStateValue = {};
        #     }
        else:
            # The finite state value of a machine without child states is just an empty object
            initial_state_value = {}

        #     this.__cache.initialStateValue = initialStateValue;
        # TODO TD implement cache
        # self.__cache.initial_state_value = initial_state_value

        #     return this.__cache.initialStateValue;
        # TODO TD implement cache
        # return self.__cache.initial_state_value
        return initial_state_value
        #   }

    def _history_value(
        self, relative_state_value: Union[StateValue, None] = None
    ) -> Union[HistoryValue, None]:

        # private historyValue(
        #     relativeStateValue?: StateValue | undefined
        #   ): HistoryValue | undefined {

        #     if (!keys(this.states).length) {
        #       return undefined;
        #     }

        if len(self.states.keys()) == 0:
            return None

        #     return {
        #       current: relativeStateValue || this.initialStateValue,
        #       states: mapFilterValues<
        #         StateNode<TContext, any, TEvent>,
        #         HistoryValue | undefined
        #       >(

        def f_iteratee(state_node: StateNode, key: str, collection: Dict = None):
            if not relative_state_value:
                return state_node._history_value()

            sub_state_value = (
                None
                if isinstance(relative_state_value, str)
                else relative_state_value.get(key, None)
            )
            return state_node._history_value(
                sub_state_value or state_node.initial_state_value
            )

        def f_predicate(state_node: StateNode):
            return state_node.history == None

        return HistoryValue(
            **{
                "current": relative_state_value or self.initial_state_value,
                "states": map_filter_values(
                    #         this.states,
                    collection=self.states,
                    iteratee=f_iteratee,
                    predicate=f_predicate,
                ),
            }
        )
        #         (stateNode, key) => {
        #           if (!relativeStateValue) {
        #             return stateNode.historyValue();
        #           }

        #           const subStateValue = isString(relativeStateValue)
        #             ? undefined
        #             : relativeStateValue[key];

        #           return stateNode.historyValue(
        #             subStateValue || stateNode.initialStateValue
        #           );
        #         },
        #         (stateNode) => !stateNode.history
        #       )
        #     };
        #   }

    @property
    def target(self) -> Union[StateValue, None]:
        """The target state value of the history state node, if it exists. This represents the
           default state value to transition to if no history value exists yet.

        Returns:
            Union[ StateValue , None ]: The target state value of the history state node
        """

        #   /**
        #    * The target state value of the history state node, if it exists. This represents the
        #    * default state value to transition to if no history value exists yet.
        #    */
        #   public get target(): StateValue | undefined {

        #     let target;
        target = None
        #     if (this.type === 'history') {
        if self.type == "history":
            #       const historyConfig = this.config as HistoryStateNodeConfig<
            #         TContext,
            #         TEvent
            #       >;
            history_config = HistoryStateNodeConfig(
                **self.config
            )  # as HistoryStateNodeConfig<
            #       if (isString(historyConfig.target)) {
            if isinstance(history_config.target, str):
                #         target = isStateId(historyConfig.target)
                #           ? pathToStateValue(
                #               this.machine
                #                 .getStateNodeById(historyConfig.target)
                #                 .path.slice(this.path.length - 1)
                #             )
                #           : historyConfig.target;
                target = (
                    path_to_state_value(
                        (
                            self.machine.root.get_state_node_by_id(
                                history_config.target
                            ).path[(self.path.length - 1)]
                        )
                    )
                    if is_state_id(history_config.target)
                    else history_config.target
                )
            #       } else {
            else:
                target = history_config.target

        #     return target;
        return target
        #   }

    def resolve_history(self, history_value: HistoryValue = None) -> List[StateNode]:
        """Resolves to the historical value(s) of the parent state node,
           represented by state nodes.

        Args:
            history_value (HistoryValue): the value to resolve

        Returns:
            List[StateNode]: historical value(s) of the parent state node
        """

        #   /**
        #    * Resolves to the historical value(s) of the parent state node,
        #    * represented by state nodes.
        #    *
        #    * @param historyValue
        #    */
        #   private resolveHistory(
        #     historyValue?: HistoryValue
        #   ): Array<StateNode<TContext, any, TEvent, any>> {
        #     if (this.type !== 'history') {
        #       return [this];
        #     }

        #     const parent = this.parent!;
        parent = self.parent  # .copy()

        #     if (!historyValue) {
        #       const historyTarget = this.target;
        #       return historyTarget
        #         ? flatten(
        #             toStatePaths(historyTarget).map((relativeChildPath) =>
        #               parent.getFromRelativePath(relativeChildPath)
        #             )
        #           )
        #         : parent.initialStateNodes;
        #     }
        if not history_value:
            history_target = self.target
            return (
                flatten(
                    [
                        parent.get_from_relative_path(relative_child_path)
                        for relative_child_path in to_state_paths(history_target)
                    ]
                )
                if history_target
                else parent.initial_state_nodes
            )

        #     const subHistoryValue = nestedPath<HistoryValue>(
        #       parent.path,
        #       'states'
        #     )(historyValue).current;

        sub_history_value = nested_path(parent.path, "states")(
            history_value.__dict__
        ).current

        #     if (isString(subHistoryValue)) {
        #       return [parent.getStateNode(subHistoryValue)];
        #     }

        if isinstance(sub_history_value, str):
            return [parent.get_state_node(sub_history_value)]

        #     return flatten(
        #       toStatePaths(subHistoryValue!).map((subStatePath) => {
        #         return this.history === 'deep'
        #           ? parent.getFromRelativePath(subStatePath)
        #           : [parent.states[subStatePath[0]]];
        #       })
        #     );
        #   }

        return flatten(
            [
                parent.get_from_relative_path(sub_state_path)
                if self.history == "deep"
                else [parent.states[sub_state_path[0]]]
                for sub_state_path in to_state_paths(sub_history_value)
            ]
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

        #   /**
        #    * Retrieves state nodes from a relative path to this state node.
        #    *
        #    * @param relativePath The relative path from this state node
        #    * @param historyValue
        #    */
        #   public getFromRelativePath(
        #     relativePath: string[]
        #   ): Array<StateNode<TContext, any, TEvent, any>> {

    def get_relative_state_nodes(
        self,
        relative_state_id: StateNode,
        history_value: HistoryValue = None,
        resolve: bool = True,
    ) -> List[StateNode]:
        """Returns the leaf nodes from a state path relative to this state node.

        Args:
            relative_state_id (StateNode): The relative state path to retrieve the state nodes
            history_value (HistoryValue, optional):The previous state to retrieve history. Defaults to None.
            resolve (bool, optional): Whether state nodes should resolve to initial child state nodes. Defaults to True.

        Raises:
            Exception: [description]
            Exception: [description]
            Exception: [description]
            Exception: [description]

        Returns:
            List[StateNode]: leaf nodes from a state path relative to this state node
        """
        #   /**
        #    * Returns the leaf nodes from a state path relative to this state node.
        #    *
        #    * @param relativeStateId The relative state path to retrieve the state nodes
        #    * @param history The previous state to retrieve history
        #    * @param resolve Whether state nodes should resolve to initial child state nodes
        #    */
        #   public getRelativeStateNodes(
        #     relativeStateId: StateNode<TContext, any, TEvent>,
        #     historyValue?: HistoryValue,
        #     resolve: boolean = true
        #   ): Array<StateNode<TContext, any, TEvent>> {

        #     return resolve
        #       ? relativeStateId.type === 'history'
        #         ? relativeStateId.resolveHistory(historyValue)
        #         : relativeStateId.initialStateNodes
        #       : [relativeStateId];
        #   }

        return (
            (
                relative_state_id.resolve_history(history_value)
                if relative_state_id.type == "history"
                else relative_state_id.initial_state_nodes
            )
            if resolve
            else [relative_state_id]
        )

    def get_from_relative_path(
        self, relative_path: Union[str, List(str)], history_value: HistoryValue = None
    ) -> List[StateNode]:

        #     if (!relativePath.length) {
        #       return [this];
        #     }
        if isinstance(relative_path, List) and len(relative_path) == 0:
            return [self]

        #     const [stateKey, ...childStatePath] = relativePath;
        state_key, *child_state_path = relative_path

        #     if (!this.states) {
        #       throw new Error(
        #         `Cannot retrieve subPath '${stateKey}' from node with no states`
        #       );
        #     }
        if self.states is None:
            msg = f"Cannot retrieve subPath '{state_key}' from node with no states"
            logger.error(msg)
            raise Exception(msg)

        #     const childStateNode = this.getStateNode(stateKey);
        child_state_node = self.get_state_node(state_key)

        #     if (childStateNode.type === 'history') {
        #       return childStateNode.resolveHistory();
        #     }
        if child_state_node.type == "history":
            return child_state_node.resolve_history(history_value)

        #     if (!this.states[stateKey]) {
        #       throw new Error(
        #         `Child state '${stateKey}' does not exist on '${this.id}'`
        #       );
        #     }

        if self.states.get(state_key, None) is None:
            msg = f"Child state '{state_key}' does not exist on '{self.id}'"
            logger.error(msg)
            raise Exception(msg)

        #     return this.states[stateKey].getFromRelativePath(childStatePath);
        return self.states[state_key].get_from_relative_path(
            child_state_path, history_value
        )

    def get_state_node(self, state_key: str) -> StateNode:
        #   public getStateNode(
        #     stateKey: string
        #   ): StateNode<TContext, any, TEvent, TTypestate> {
        #   /**
        #    * Returns the child state node from its relative `stateKey`, or throws.
        #    */
        """Returns the child state node from its relative `stateKey`, or raises exception.

        Args:
            state_key (str): [description]

        Returns:
            StateNode: Returns the child state node from its relative `stateKey`, or throws.
        """
        #     if (isStateId(stateKey)) {
        if is_state_id(state_key):
            return self.machine.get_state_node_by_id(state_key)
        #     }

        #     if (!this.states) {
        if not self.states:
            #       throw new Error(
            #         `Unable to retrieve child state '${stateKey}' from '${this.id}'; no child states exist.`
            #       );
            msg = f"Unable to retrieve child state '{state_key}' from '{self.id}'; no child states exist."
            logger.error(msg)
            raise Exception(msg)

        #     const result = this.states[stateKey];
        result = self.states.get(state_key, None)
        #     if (!result) {
        if not result:
            #       throw new Error(
            #         `Child state '${stateKey}' does not exist on '${this.id}'`
            #       );
            msg = f"Child state '{state_key}' does not exist on '{self.id}'"
            logger.error(msg)
            raise Exception(msg)

        #     return result;
        return result

    def get_state_nodes(self, state: StateValue) -> List[StateNode]:
        #   public getStateNodes(
        #     state: StateValue | State<TContext, TEvent, any, TTypestate>
        #   ): Array<StateNode<TContext, any, TEvent, TTypestate>> {
        # /**
        #    * Returns the state nodes represented by the current state value.
        #    *
        #    * @param state The state value or State instance
        #    */
        """Returns the state nodes represented by the current state value.

        Args:
            state (StateValue): The state value or State instance

        Raises:
            Exception: [description]

        Returns:
            List[StateNode]: Returns the state nodes represented by the current state value.
        """
        #     if (!state) {
        #       return [];
        #     }
        if state is None:
            return []

        #     const stateValue =
        #       state instanceof State
        #         ? state.value
        #         : toStateValue(state, this.delimiter);
        state_value = (
            state.value
            if isinstance(state, State)
            else to_state_value(state, self.delimiter)
        )

        #     if (isString(stateValue)) {
        if isinstance(state_value, str):

            #       const initialStateValue = this.getStateNode(stateValue).initial;
            initial_state_value = self.get_state_node(state_value).initial

            #       return initialStateValue !== undefined
            #         ? this.getStateNodes({ [stateValue]: initialStateValue } as StateValue)
            #         : [this, this.states[stateValue]];
            #     }
            # TODO: WIP Check this -
            return (
                self.get_state_nodes({[state_value]: initial_state_value})
                if initial_state_value
                else [self, self.states[state_value]]
            )

        #     const subStateKeys = keys(stateValue);
        sub_state_keys = state_value.keys()

        #     const subStateNodes: Array<
        #       StateNode<TContext, any, TEvent, TTypestate>
        #     > = subStateKeys.map((subStateKey) => this.getStateNode(subStateKey));
        sub_state_nodes: List[StateNode] = [
            self.get_state_node(sub_state_key) for sub_state_key in sub_state_keys
        ]

        #     subStateNodes.push(this);
        sub_state_nodes.append(self)

        #     return subStateNodes.concat(

        # def full_union(input):
        #     """ Compute the union of a list of sets """
        #     return reduce(set.union, input[1:], input[0])

        # result = full_union(L)

        #       subStateKeys.reduce((allSubStateNodes, subStateKey) =>
        # {
        #         const subStateNode = this.getStateNode(subStateKey).getStateNodes(
        #           stateValue[subStateKey]
        #         );
        def reduce_fx(all_sub_state_nodes, sub_state_key):
            sub_state_node = self.get_state_node(sub_state_key).get_state_nodes(
                state_value[sub_state_key]
            )
            all_sub_state_nodes.extend(sub_state_node if sub_state_node else [])
            return all_sub_state_nodes

        def substate_node_reduce(sub_state_keys):
            initial_list = []
            result_list = reduce(reduce_fx, sub_state_keys, initial_list)
            return result_list

        #       }, [] as Array<StateNode<TContext, any, TEvent, TTypestate>>)
        #     );
        reduce_results = substate_node_reduce(sub_state_keys)
        sub_state_nodes.extend(reduce_results)
        return sub_state_nodes

    #   /**
    #    * Returns `true` if this state node explicitly handles the given event.
    #    *
    #    * @param event The event in question
    #    */
    #   public handles(event: Event<TEvent>): boolean {
    #     const eventType = getEventType<TEvent>(event);

    #     return this.events.includes(eventType);
    #   }

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
        has_non_last_unguarded_target = any(
            [
                (
                    "cond" not in transition
                    and "in" not in transition
                    and (
                        isinstance(transition.target, str)
                        or is_machine(transition.target)
                    )
                )
                for transition in transitions[0:-1]
            ]
        )

        # .slice(0, -1)
        # .some(
        #   (transition) =>
        #     !('cond' in transition) &&
        #     !('in' in transition) &&
        #     (isString(transition.target) || isMachine(transition.target))
        # );

        #   const eventText =
        #     event === NULL_EVENT ? 'the transient event' : `event '${event}'`;
        eventText = "the transient event" if event == NULL_EVENT else f"event '{event}'"

        #   warn(
        #     !hasNonLastUnguardedTarget,
        #     `One or more transitions for ${eventText} on state '${stateNode.id}' are unreachable. ` +
        #       `Make sure that the default transition is the last one defined.`
        #   );
        if not has_non_last_unguarded_target:
            logger.warning(
                (
                    f"One or more transitions for {eventText} on state '{state_node.id}' are unreachable. "
                    f"Make sure that the default transition is the last one defined."
                )
            )

    #  /**
    #    * Returns the relative state node from the given `statePath`, or throws.
    #    *
    #    * @param statePath The string or string array relative path to the state node.
    #    */
    #   public getStateNodeByPath(
    #     statePath: string | string[]
    #   ): StateNode<TContext, any, TEvent, any> {

    def get_state_node_by_path(self, state_path: str) -> StateNode:
        """Returns the relative state node from the given `statePath`, or throws.

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

        if isinstance(state_path, str) and is_state_id(state_path):
            try:
                return self.get_state_node_by_id(state_path[1:].copy())
            except Exception as e:
                # // try individual paths
                # // throw e;
                pass

            #     const arrayStatePath = toStatePath(statePath, this.delimiter).slice();
            array_state_path = to_state_path(state_path, self.delimiter)[:].copy()
            #     let currentStateNode: StateNode<TContext, any, TEvent, any> = this;
            current_state_node = self

            #     while (arrayStatePath.length) {
            while len(array_state_path) > 0:
                #       const key = arrayStatePath.shift()!;
                key = (
                    array_state_path.pop()
                )  # TODO check equivaelance to js .shift()! , https://www.typescriptlang.org/docs/handbook/release-notes/typescript-2-0.html#non-null-assertion-operator
                #       if (!key.length) {
                #         break;
                #       }

                if len(key) == 0:
                    break

                #       currentStateNode = currentStateNode.getStateNode(key);
                current_state_node = current_state_node.get_state_node(key)

            #     return currentStateNode;
            return current_state_node

    #   private resolveTarget(
    #     _target: Array<string | StateNode<TContext, any, TEvent>> | undefined
    #   ): Array<StateNode<TContext, any, TEvent>> | undefined {

    def resolve_target(_target: List[StateNode]) -> List[StateNode]:

        #     if (_target === undefined) {
        #       // an undefined target signals that the state node should not transition from that state when receiving that event
        #       return undefined;
        #     }
        if not _target:
            #    an undefined target signals that the state node should not transition from that state when receiving that event
            return None

        #     return _target.map((target) =>
        def function(self, target):
            #       if (!isString(target)) {
            #         return target;
            #       }
            if isinstance(target, str):
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
            if is_internal_target and not self.parent:
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

            if self.parent:
                try:
                    target_state_node = self.parent.get_state_node_by_path(
                        resolved_target
                    )
                    return target_state_node
                except Exception as e:
                    msg = f"Invalid transition definition for state node '{self.id}':\n{e}"
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

    def format_transition(
        self, transition_config: TransitionConfig
    ) -> TransitionDefinition:

        #     const normalizedTarget = normalizeTarget(transitionConfig.target);
        normalized_target = normalize_target(transition_config["target"])

        #     const internal =
        #       'internal' in transitionConfig
        #         ? transitionConfig.internal
        #         : normalizedTarget
        #         ? normalizedTarget.some(
        #             (_target) => isString(_target) && _target[0] === this.delimiter
        #           )
        #         : true;
        internal = (
            transition_config["internal"]
            if "internal" in transition_config
            else any(
                isinstance(_target, str) and _target[0] == self.delimiter
                for _target in normalized_target
            )
            if normalized_target
            else True
        )

        #     const { guards } = this.machine.options;
        guards = self.machine.options["guards"]
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
                "actions": to_action_objects(to_array(transition_config["actions"])),
                "cond": to_guard(transition_config.cond, guards),
                **target,
                "source": self,
                **internal,
                "eventType": transition_config.event,
                "toJSON": None,
            },
        }
        transition = {
            **transition,
            **{
                "target": ["#{t.id}" for t in transition.target]
                if transition.target
                else None,
                "source": "#{self.id}",
            },
        }

        #     return transition;
        return transition

    def format_transitions(self) -> List:
        #   StateNode.prototype.formatTransitions = function () {
        #     var e_9, _a;

        #     var _this = this;
        _self = self

        onConfig = None

        #     if (!this.config.on) {
        #       onConfig = [];
        if "on" not in self.config:
            onConfig = {}

        #     } else if (Array.isArray(this.config.on)) {
        #       onConfig = this.config.on;
        elif isinstance(self.config, dict):
            onConfig = self.config["on"]
        #     } else {
        else:
            # TODO: TD implement WILDCARD
            #       var _b = this.config.on,
            #           _c = WILDCARD,
            #           _d = _b[_c],
            #           wildcardConfigs = _d === void 0 ? [] : _d,
            wildcard_configs = []  # Workaround for #TODO: TD implement WILDCARD
            #           strictTransitionConfigs_1 = _tslib.__rest(_b, [typeof _c === "symbol" ? _c : _c + ""]);
            # TODO: TD implement and tslib.__rest functionationality
            # strictTransitionConfigs_1 = _tslib.__rest(_b, [typeof _c === "symbol" ? _c : _c + ""])
            strict_transition_configs_1 = self.config["on"]

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
                logger.warning(
                    (
                        f"Empty string transition configs (e.g., `{{ on: {{ '': ... }}}}`) for transient transitions are deprecated. "
                        f"Specify the transition in the `{{ always: ... }}` property instead. "
                        f'Please check the `on` configuration for "#{self.id}".'
                    )
                )
                transition_config_array = to_transition_config_array(
                    key, strict_transition_configs_1[key]
                )

                if not IS_PRODUCTION:
                    self.validate_arrayified_transitions(
                        self, key, transition_config_array
                    )

                return transition_config_array

        #       onConfig = utils.flatten(utils.keys(strictTransitionConfigs_1).map(
        # ).concat(utils.toTransitionConfigArray(WILDCARD, wildcardConfigs)));
        #     }

        on_config = flatten(
            [function(key) for key in strict_transition_configs_1.keys()].append(
                to_transition_config_array(WILDCARD, wildcard_configs)
            )
        )

        #     var eventlessConfig = this.config.always ? utils.toTransitionConfigArray('', this.config.always) : [];
        eventless_config = (
            to_transition_config_array("", self.config["always"])
            if "always" in self.config
            else []
        )

        #     var doneConfig = this.config.onDone ? utils.toTransitionConfigArray(String(actions.done(this.id)), this.config.onDone) : [];
        done_config = (
            to_transition_config_array(str(done(self.id)), self.config["onDone"])
            if "onDone" in self.config
            else []
        )

        #     if (!environment.IS_PRODUCTION) {
        #       utils.warn(!(this.config.onDone && !this.parent), "Root nodes cannot have an \".onDone\" transition. Please check the config of \"" + this.id + "\".");
        #     }
        if IS_PRODUCTION and not ("onDone" in self.config and not self.parent):

            logger.warning(
                f'Root nodes cannot have an ".onDone" transition. Please check the config of "{self.id}".'
            )

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
                        str(done_invoke(invoke_def.id)), invoke_def["onDone"]
                    )
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
                        str(done_invoke(invoke_def.id)), invoke_def["onError"]
                    )
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
        formatted_transitions = flatten(
            [
                #       toArray(transitionConfig).map((transition) =>
                #         this.formatTransition(transition)
                self.format_transition(transition)
                for transition in [
                    transition_config
                    #     (
                    #       transitionConfig: TransitionConfig<TContext, TEvent> & {
                    #         event: TEvent['type'] | NullEvent['type'] | '*';
                    #       }
                    #     ) =>
                    for transition_config in [
                        done_config,
                        invoke_config,
                        on_config,
                        eventless_config,
                    ]
                ]
            ]
        )

        # for (const delayedTransition of delayedTransitions) {
        #   formattedTransitions.push(delayedTransition as any);
        # }
        for delayed_transition in delayed_transitions:
            formatted_transitions.append(delayed_transition)

        [
            formatted_transitions.append(delayed_transition)
            for delayed_transition in delayed_transitions
        ]

        return formatted_transitions

    #   Object.defineProperty(StateNode.prototype, "transitions", {
    # TODO: this clashes with the attribute `transition` so relabelled to `get_transitions` need to understand this property in relation to the attribute, how does format_transitions work
    @property
    def get_transitions(self) -> List:
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
