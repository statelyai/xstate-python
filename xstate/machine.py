from xstate.state_node import StateNode


class Machine:
    def __init__(self, config):
        self.id = config["id"]
        self._id_map = {}
        self.states = {
            k: StateNode(v, parent=self, machine=self)
            for k, v in config.get("states", {}).items()
        }

