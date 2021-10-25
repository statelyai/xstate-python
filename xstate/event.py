from __future__ import (
    annotations,
)  #  PEP 563:__future__.annotations will become the default in Python 3.11
from typing import Dict, Optional


class Event:
    name: str
    data: Dict

    def __init__(self, name: str, data: Optional[Dict] = None):
        self.name = name
        self.data = data

    def __repr__(self) -> str:
        return repr({"name": self.name, "data": self.data})
