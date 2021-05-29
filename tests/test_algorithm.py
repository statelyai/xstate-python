from xstate.algorithm import is_parallel_state
from xstate.machine import Machine


def test_is_parallel_state():
    machine = Machine(
        {"id": "test", "initial": "foo", "states": {"foo": {"type": "parallel"}}}
    )

    foo_state_node = machine._get_by_id("test.foo")

    assert is_parallel_state(foo_state_node) is True


def test_is_not_parallel_state():
    machine = Machine(
        {"id": "test", "initial": "foo", "states": {"foo": {"type": "atomic"}}}
    )

    foo_state_node = machine._get_by_id("test.foo")

    assert is_parallel_state(foo_state_node) is False
