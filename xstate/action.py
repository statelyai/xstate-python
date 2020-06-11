from typing import Callable, Optional, Dict, Any


def not_implemented():
    pass


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
