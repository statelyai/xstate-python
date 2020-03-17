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
    print([target.id for target in lights.root.initial.target])
    print([item.id for item in lights._get_configuration({"red": "walk"})])

    assert (
        lights.transition(State("green", {}), "TIMER")[0].id
        == "lights.yellow"
    )
