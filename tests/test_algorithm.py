"""Tests for  algorithims

These tests use either machines coded as python `dict` 
or accept strings representing xstate javascript/typescript which are
then converted to a python `dict` by the module `js2py`

The following tests exist
    * test_is_parallel_state - returns the column headers of the file
    * test_is_not_parallel_state - the main function of the script
"""

import pytest
from .utils_for_tests import pytest_func_docstring_summary


from xstate.algorithm import is_parallel_state, to_state_path, get_configuration
from xstate.machine import Machine


class TestAlgorithims:

    test_machine = Machine(
        """    {
            id: 'a',
            initial: 'b1',
            states: {
                b1: {
                id: 'b1',
                type: 'parallel',
                states: {
                    c1: {
                    id: 'c1',
                    initial: 'd1',
                    states: {
                        d1: { id: 'd1' },
                        d2: {
                        id: 'd2',
                        initial: 'e1',
                        states: {
                            e1: { id: 'e1' },
                            e2: { id: 'e2' }
                        }
                        }
                    }
                    },
                    c2: { id: 'c2' },
                    c3: {
                    id: 'c3',
                    initial: 'd3',
                    states: {
                        d3: { id: 'd3' },
                        d4: {
                        id: 'd4',
                        initial: 'e3',
                        states: {
                            e3: { id: 'e3' },
                            e4: { id: 'e4' }
                        }
                        }
                    }
                    }
                }
                },
                b2: {
                id: 'b2',
                initial: 'c4',
                states: {
                    c4: { id: 'c4' }
                }
                },
                b3: {
                id: 'b3',
                initial: 'c5',
                states: {
                    c5: { id: 'c5' },
                    c6: {
                    id: 'c6',
                    type: 'parallel',
                    states: {
                        d5: { id: 'd5' },
                        d6: { id: 'd6' },
                        d7: { id: 'd7' }
                    }
                    }
                }
                }
            }
            }
        """
    )

    def test_algorithim_get_configuration(self, request):
        """1 - getConfiguration

        ref: https://github.com/statelyai/xstate/blob/main/packages/core/test/algorithm.test.ts
        """
        prev_nodes = self.test_machine.root.get_state_nodes(
            # TODO: Should this be a config snippet `StateNode.get_state_nodes` does not decode dict
            """    {
                            b1: {
                                c1: 'd1',
                                c2: {},
                                c3: 'd3'
                            }
                            }
                        """
        )
        nodes = [self.test_machine.root.get_state_node_by_id(id) for id in ["c1", "d4"]]

        c = get_configuration(prev_nodes, nodes)

        assert [sn.id for sn in c].sort() == [
            "a",
            "b1",
            "c1",
            "c2",
            "c3",
            "d1",
            "d4",
            "e3",
        ], pytest_func_docstring_summary(request)


def test_machine_config_translate():

    xstate_js_config = """{
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
        """
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


class TestStatePaths:
    def test__to_state_path(self, request):
        """should have valid results for converstion to state paths list"""
        assert to_state_path("one.two.three") == ["one", "two", "three"]
        assert to_state_path("one/two/three", delimiter="/") == ["one", "two", "three"]
        assert to_state_path(["one", "two", "three"]) == ["one", "two", "three"]
        try:
            state_id = {"values": ["one", "two", "three"]}
            assert to_state_path(state_id) == ["one", "two", "three"]
        except Exception as e:
            assert (
                e.args[0]
                == "{'values': ['one', 'two', 'three']} is not a valid state path"
            )
