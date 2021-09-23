from typing import TYPE_CHECKING, Any, Callable, List, NamedTuple, Optional, Union

# from xstate.algorithm import (
#     get_configuration_from_js
# )
# TODO: Work around for import error, don't know why lint unresolved, if import from xstate.algorthim
# Explain : ImportError: cannot import name 'get_configuration_from_js' from 'xstate.algorithm' 
from xstate.utils import (
    get_configuration_from_js
)


from xstate.action import Action
from xstate.event import Event

if TYPE_CHECKING:
    from xstate.state_node import StateNode

CondFunction = Callable[[Any, Event], bool]


class TransitionConfig(NamedTuple):
    target: List[str]


class Transition:
    event: str
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
        if isinstance(config,str) and config.lstrip()[0]=="{" and config.rstrip()[-1]=="}":
            try:
                config = get_configuration_from_js(config)
            except Exception as e:
                raise f"Invalid snippet of Javascript for Machine configuration, Exception:{e}"

        self.event = event
        self.config = config
        self.source = source
        self.type = "external"
        self.cond = config.get("cond", None) if isinstance(config, dict) else None
        self.order = order

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
    def target(self) -> List["StateNode"]:
        if isinstance(self.config, str):
            return [self.source._get_relative(self.config)]
        elif isinstance(self.config, dict):
            if isinstance(self.config["target"], str):
                return [self.source._get_relative(self.config["target"])]

            return [self.source._get_relative(v) for v in self.config["target"]]
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
