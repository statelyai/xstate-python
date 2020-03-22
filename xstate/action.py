from typing import Callable, Optional


def not_implemented():
    pass


class Action:
    type: str
    exec: Callable[[], None]

    def __init__(self, type: str, exec: Optional[Callable[[], None]] = not_implemented):
        self.type = type
        self.exec = exec

    def __repr__(self):
        return repr({"type": self.type})
