#!/usr/bin/env python3

from xstate.machine import Machine
import time

# Trafic light example
# green -> yellow -> red -> green ..
timing = 2

def enterGreen():
    print("\tENTER_GREEN callback")
def exitGreen():
    print("\tEXIT_GREEN callback")

lights = Machine(
    {
        "id": "lights",
        "initial": "green",
        "states": {
            "green": {
                "on": {"TIMER": "yellow"}, 
                "entry": [{"type": "enterGreen"}], 
                "exit": [{"type": "exitGreen"}]
            },
            "yellow": {
                "on": {"TIMER": "red"}, 
                "entry": [{"type": "enterYellow"}]
            },
            "red": {
                "on": {"TIMER": "green"},
                "entry": [
                    lambda: print("\tINLINE callback")
                ]
            },
        },
    },
    actions={
        # action implementations
        "enterGreen": enterGreen,
        "exitGreen": exitGreen,
        "enterYellow": lambda: print("\tENTER_YELLOW callback")
    }
)

if __name__ == "__main__":
    state = lights.initial_state
    
    for i in range(10):
        # execute all the actions (before/exit states)
        for action in state.actions: action()
        print("VALUE: {}".format(state.value))
        
        time.sleep(timing)
        state = lights.transition(state, "TIMER")