"""Tests for  algorithims

These tests use either machines coded as python `dict` 
or accept strings representing xstate javascript/typescript which are
then converted to a python `dict` by the module `js2py`

The following tests exist
    * test_is_parallel_state - returns the column headers of the file
    * test_is_not_parallel_state - the main function of the script
"""
from xstate.algorithm import is_parallel_state
from xstate.machine import Machine


def test_machine_config_translate():

    xstate_js_config =    '''{
                id: 'fan',
                initial: 'off',
                states: {
                    off: {
                    on: {
                        POWER:'on.hist',
                        H_POWER:'on.H',
                        SWITCH:'on.first'
                    }

                    },
                    on: {
                    initial: 'first',
                    states: {
                        first: {
                        on: {
                            SWITCH:'second'
                        }
                        },
                        second: {
                        on: {
                            SWITCH: 'third'
                        }
                        },
                        third: {},
                        H: {
                        type: 'history'
                        },
                        hist: {
                        type: 'history',
                        history:'shallow'
                        },
                    }
                    }
                }
        }
        '''
    # xstate_python_config=machine_config_translate(xstate_js_config)
    # assert isinstance(xstate_python_config,dict)
    try:
        machine = Machine(xstate_js_config)
    except Exception as e:
        assert False, f"Machine config is not valid, Exception:{e}"

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
