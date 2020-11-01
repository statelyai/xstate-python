from __future__ import annotations
from typing import List, Union, Any, NamedTuple, Callable, TYPE_CHECKING
from xstate.action import Action
from xstate.event import Event

if TYPE_CHECKING:
    from xstate.state_node import StateNode

CondFunction = Callable[[Any, Event], bool]


class TransitionConfig(NamedTuple):
    target: List[str]


class Transition:
    event: str
    source: StateNode
    config: Union[str, StateNode, TransitionConfig]
    actions: List[Action]
    cond: Optional[CondFunction]
    # "internal" or "external"
    type: str

    def __init__(
        self, config, source: StateNode, event: str, cond: Optional[CondFunction] = None
    ):
        self.event = event
        self.config = config
        self.source = source
        self.type = "external"
        self.cond = cond

        self.actions = (
            (
                [
                    Action(type=action.get("type"), data=action)
                    for action in config.get("actions", [])
                ]
            )
            if isinstance(config, dict)
            else []
        )

    @property
    def target(self) -> List[StateNode]:
        if isinstance(self.config, str):
            return [self.source._get_relative(self.config)]
        elif isinstance(self.config, dict):
            if isinstance(self.config["target"], str):
                return [self.source._get_relative(self.config["target"])]

            return [self.source._get_relative(v) for v in self.config["target"]]
        else:
            return [self.config] if self.config else []

