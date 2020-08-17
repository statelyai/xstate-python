from xstate.machine import Machine
from xstate.state import State


lights = Machine(
    {
        "id": "lights",
        "initial": "green",
        "states": {
            "green": {
                "on": {"TIMER": "yellow"},
                "entry": [{"type": "enterGreen"}]
            },
            "yellow": {"on": {"TIMER": "red"}},
            "red": {
                "initial": "walk",
                "states": {
                    "walk": {"on": {"COUNTDOWN": "wait"}},
                    "wait": {"on": {"COUNTDOWN": "stop"}},
                    "stop": {"on": {"TIMEOUT": "timeout"}},
                    "timeout": {"type": "final"},
                },
                "onDone": "green",
            },
        },
    }
)


def test_machine():
    yellow_state = lights.transition(lights.initial_state, "TIMER")

    assert yellow_state.value == "yellow"

    red_state = lights.transition(yellow_state, "TIMER")

    assert red_state.value == {"red": "walk"}


def test_machine_initial_state():
    state = lights.initial_state

    assert lights.initial_state.value == "green"


def test_final_state():
    red_stop_state = lights.state_from({"red": "stop"})

    red_timeout_state = lights.transition(red_stop_state, "TIMEOUT")

    assert red_timeout_state.value == "green"
