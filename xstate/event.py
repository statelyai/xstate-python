from typing import Dict

class Event:
    name: str
    data: Dict
    
    def __init__(self, name: str, data: Dict):
        self.name = name
        self.data = data
