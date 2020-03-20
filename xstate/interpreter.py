from xstate.machine import Machine
from xstate.state import State


class Interpreter:
    machine: Machine
    state: State

    def __init__(self, machine):
        self.machine = machine
        self.state = self.machine.initial_state

    def start():
        pass
