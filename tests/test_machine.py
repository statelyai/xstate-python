from xstate.machine import Machine

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
    assert Machine(example).states["bar"].on["TOUCH"].target[0].id == "blahblahblah"
