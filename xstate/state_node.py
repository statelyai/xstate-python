from xstate.transition import Transition


class StateNode:
    def __init__(self, config, machine, parent=None):
        self.parent = parent
        self.id = config.get("id", machine.id + "." + config["key"])
        self.machine = machine
        self.machine._id_map[self.id] = self
        self.key = config["key"]
        self.states = {
            k: StateNode(v, machine=machine, parent=self)
            for k, v in config.get("states", {}).items()
        }
        self.on = {
            k: Transition(v, state_node=self) for k, v in config.get("on", {}).items()
        }

