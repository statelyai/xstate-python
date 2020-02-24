class Transition:
    def __init__(self, config, state_node):
        self.config = config
        self.source = state_node

    @property
    def target(self):
        return [self.source.machine._id_map.get(v) for v in self.config["target"]]
