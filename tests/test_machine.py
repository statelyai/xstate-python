from xstate.machine import Machine
from xstate.state import State

example = {
    "key": "foo",
    "id": "machine.foo",
    "states": {
        "bar": {
            "key": "bar",
            "id": "machine.foo.bar",
            "on": {"TOUCH": {"target": ["machine.foo.baz"]}},
        },
        "baz": {"key": "baz"},
    },
}


def test_machine():
    print(
        [
            t.id
            for t in Machine(example).transition(State("bar", {"foo": "bar"}), "TOUCH")
        ]
    )
    assert (
        Machine(example).transition(State("bar", {"foo": "bar"}), "TOUCH")[0].id
        == "machine.foo.baz"
    )
