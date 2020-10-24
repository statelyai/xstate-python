from typing import Dict, Optional, Union


class Event:
    name: str
    data: Dict

    def __init__(self, name: str, data: Optional[Dict] = None):
        self.name = name
        self.data = data

    def __repr__(self) -> str:
        return repr({"name": self.name, "data": self.data})
