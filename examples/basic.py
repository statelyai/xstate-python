#!/usr/bin/env python3

from xstate.machine import Machine
import time


# Trafic light example
# green -> yellow -> red -> green ..

lights = Machine(
    {
        "id": "lights",
        "initial": "green",
        "states": {
            "green": {"on": {"TIMER": "yellow"},},
            "yellow": {"on": {"TIMER": "red"}},
            "red": {"on": {"TIMER": "green"}},
        },
    }
)

if __name__ == "__main__":
    state = lights.initial_state
    print(state.value)
    time.sleep(0.5)
    
    for i in range(10):
        state = lights.transition(state, "TIMER")
        print(state.value)
        time.sleep(0.5)
        
        state = lights.transition(state, "TIMER")
        print(state.value)
        time.sleep(0.5)
        
        state = lights.transition(state, "TIMER")
        print(state.value)
        time.sleep(0.5)