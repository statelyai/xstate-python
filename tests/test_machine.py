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
            "green": {"on": {"TIMER": "yellow"}},
            "yellow": {"on": {"TIMER": "red"}},
            "red": {"states": {"walk": {}, "wait": {}, "stop": {}}},
        },
    }
)


def test_machine():
    assert lights.transition(State("green", {}), "TIMER")[0].id == "lights.yellow"


def test_machine_initial_state():
    print(lights.initial_state())
