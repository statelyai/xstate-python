from xstate.machine import Machine
from xstate.state import State

example = {
    "key": "foo",
    "id": "machine.foo",
    "states": {"bar": {"on": {"TOUCH": "baz"},}, "baz": {},},
}

lights = Machine(
    {
        "key": "lights",
        "id": "lights",
        "initial": "green",
        "states": {
            "green": {
                "entry": [{"type": "firstAction"}],
                "initial": "first",
                "states": {"first": {}},
                "on": {"TIMER": "yellow"},
            },
            "yellow": {"on": {"TIMER": "red"}},
            "red": {"states": {"walk": {}, "wait": {}, "stop": {}}},
        },
    }
)


def test_machine():
    assert lights.transition(lights.initial_state, "TIMER").value == "yellow"


def test_machine_initial_state():
    state = lights.initial_state

    assert lights.initial_state.value == {"green": "first"}
