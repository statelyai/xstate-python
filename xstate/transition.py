from __future__ import (
    annotations,
)  #  PEP 563:__future__.annotations will become the default in Python 3.11
from typing import TYPE_CHECKING, Any, Callable, List, NamedTuple, Optional, Union

import xstate.algorithm as algorithm


from xstate.action import to_action_objects
from xstate.event import Event
from xstate.types import HistoryValue, StateValue

if TYPE_CHECKING:
    from xstate.action import Action
    from xstate.state_node import StateNode

CondFunction = Callable[[Any, Event], bool]


class TransitionConfig(NamedTuple):
    target: List[str]


class Transition:
    event: str
    # _event: SCXML.Event       #TODO Implement
    source: "StateNode"
    config: Union[str, "StateNode", TransitionConfig]
    actions: List[Action]
    cond: Optional[CondFunction]
    order: int
    # "internal" or "external"
    type: str

    def __init__(
        self,
        config,
        source: "StateNode",
        event: str,
        order: int,
        cond: Optional[CondFunction] = None,
    ):
        if (
            # Test for possible snippet of JS being the configuration
            isinstance(config, str)
            and config.lstrip()[0] == "{"
            and config.rstrip()[-1] == "}"
        ):
            try:
                config = algorithm.get_configuration_from_js(config)
            except Exception as e:
                raise f"Invalid snippet of Javascript for Machine configuration, Exception:{e}"

        self.event = event
        # self._event = utils.toSCXMLEvent(event) #TODO Implement
        self.config = config
        self.source = source
        self.type = "external"
        self.cond = config.get("cond", None) if isinstance(config, dict) else None
        self.order = order

        self.actions = (
            to_action_objects(config.get("actions", []), action_function_map=None)
            if isinstance(config, dict)
            else []
        )

    @property
    def target(self) -> List["StateNode"]:
        if isinstance(self.config, str) and not algorithm.is_state_id(self.config):
            return self.source.parent.get_from_relative_path(
                algorithm.to_state_path(self.config)
            )
            # return [self.source._get_relative(self.config)]
        elif isinstance(self.config, str) and algorithm.is_state_id(self.config):
            return [self.source.machine.root.get_state_node(self.config)]
        elif isinstance(self.config, dict):
            if isinstance(self.config["target"], str):
                return [self.source._get_relative(self.config["target"])]

            return [self.source._get_relative(v) for v in self.config["target"]]
        else:
            return [self.config] if self.config else []

    def target_consider_history(self, history_value: HistoryValue) -> List["StateNode"]:
        # TODO: P2, would be desirable to amalgate `target` and `target_consider_history` however the history_value would need to be an attribute of `transition` or possibly `source` ?
        # if isinstance(self.config, str):
        #     return self.source.parent.get_from_relative_path(
        #         algorithm.to_state_path(self.config), current_state.history_value
        #     )
        if isinstance(self.config, str) and not algorithm.is_state_id(self.config):
            return self.source.parent.get_from_relative_path(
                algorithm.to_state_path(self.config), history_value
            )
            # return [self.source._get_relative(self.config)]
        elif isinstance(self.config, str) and algorithm.is_state_id(self.config):
            return [self.source.machine.root.get_state_node(self.config, history_value)]
        elif isinstance(self.config, dict):
            if isinstance(self.config["target"], str):
                return [self.source._get_relative(self.config["target"], history_value)]

            return [
                self.source._get_relative(
                    v,
                    history_value,
                )
                for v in self.config["target"]
            ]
        else:
            return [self.config] if self.config else []

    def __repr__(self) -> str:
        return repr(
            {
                "event": self.event,
                "source": self.source.id,
                "target": [f"#{t.id}" for t in self.target],
                "cond": self.cond,
                "actions": self.actions,
                "type": self.type,
                "order": self.order,
            }
        )
