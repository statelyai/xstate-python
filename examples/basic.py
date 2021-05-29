#!/usr/bin/env python3

# add parent to the path to include local xstate module
import sys

sys.path.insert(0, "..")

import time

from xstate import Machine

# Trafic light example
# green -> yellow -> red -> green ..

lights = Machine(
    {
        "id": "lights",
        "initial": "green",
        "states": {
            "green": {
                "on": {"TIMER": "yellow"},
            },
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
