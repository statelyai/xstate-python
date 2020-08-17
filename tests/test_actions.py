from xstate.machine import Machine
from xstate.state import State
from unittest.mock import Mock


entry_mock = Mock()
exit_mock = Mock()

machine = Machine(
    {
        "id": "machine",
        "initial": "on",
        "states": {
            "on" : {
                "on": {"TOGGLE": "off"},
                "entry": [{"type": "entry_action"}],
                "exit": [{"type": "exit_action"}]
            },
            "off": {
                "on": {"TOGGLE": "on"}
            }
        },
    },
    actions = {
        "entry_action": entry_mock,
        "exit_action": exit_mock,
    }
)


def test_context():
    state = machine.initial_state
    assert state.value is "on"
    
    for action in state.actions:
        action()
    
    entry_mock.assert_called_with()
    assert entry_mock.call_count is 1
    assert exit_mock.call_count is 0
    
    # ------------------------
    
    state = machine.transition(state, "TOGGLE")
    
    assert state.value is "off"
    
    for action in state.actions:
        action()
    
    exit_mock.assert_called_with()
    assert entry_mock.call_count is 1
    assert exit_mock.call_count is 1
    
    